import datetime
import re
from spyderpro.pool.threadpool import ThreadPool
from spyderpro.complete_data._complete_data_interface import CompleteDataInterface
from spyderpro.data_requests.traffic.baidutraffic import BaiduTraffic
from spyderpro.data_requests.traffic.gaodetraffic import GaodeTraffic


class CompleteTraffic(CompleteDataInterface):
    """
        缓存数据：
        日常交通拥堵延迟指数：key= "traffic:{0}".format(region_id),mapping ={"HH:MM:SS":rate,....}
        道路交通数据：key ="road:{pid}:{road_id}".format(pid=region_id, road_id=roadid)
                        value =str( {
                            "pid": pid, "roadname": roadname, "up_date": up_date, "speed": speed,
                            "direction": direction, "bounds": bound, "data": data,
                            "roadpid": roadid, "rate": rate
                        })
        季度交通数据：key = "yeartraffic:{pid}".format(pid=region_id) ,value={'yyyymmdd':rate,....}
    """

    def type_daily_citytraffic_check(self, city_type: int, now_time: datetime, time_interval: datetime.timedelta,
                                     time_difference: int):
        """
        检查城市实时交通拥堵延迟指数数据是否完整
        :param city_type:0表示百度交通，1表示高德交通
        :param now_time:此时时间
        :param time_interval:city_type 为0 是5分钟时间间隔，1时30分钟
        :param time_difference:允许的时间差
        :return:
        """
        # 从mysql生产的完整的key模板
        complete_keys_regular = "traffic:%d"
        # 从redis查询的keys模板
        search_regular = "traffic:*"
        sql = None
        if city_type == 0:

            sql = "select pid from digitalsmart.citymanager where pid<1000"
        elif city_type == 1:
            sql = "select pid from digitalsmart.citymanager where pid>1000"
        complete_keys = self.get_complete_keys(sql, complete_keys_regular, search_regular)
        check_status = True  # 判断是否补漏数据
        for key in complete_keys:
            # 获取缓存的数据
            redis_data = self.redis_worke.hash_get_all(key)
            # 检查数据是否完整
            check_status = self.check_data_complete(list(redis_data.keys()), time_interval)
            if not check_status:
                break
        # 相差time_difference秒必须检查数据完整性
        if self.time_difference(now_time, complete_keys) > time_difference or not check_status:
            result = self._check_citytraffic_complete(complete_keys)
            return result
        return True

    def _check_citytraffic_complete(self, complete_keys: list) -> bool:
        """
        提交补漏数据请求
        :param complete_keys: 缓存key
        :return:
        """
        thread_pool = ThreadPool(max_workers=10)
        for key in complete_keys:
            thread_pool.submit(self._complete_citytraffic_data, key)
        thread_pool.run()
        thread_pool.close()

        return True

    def _complete_citytraffic_data(self, key: str):
        """
        请求并补全缺失的数据

        :param key: 缓存key
        :return:
        """
        time_interval = datetime.timedelta(minutes=60)

        citycode = int(re.match("traffic:(\d+)", key).group(1))  # 城市id
        if citycode > 1000:
            traffic = GaodeTraffic()
        else:
            traffic = BaiduTraffic()
        # 请求数据
        dailytraffic_iter = traffic.city_daily_traffic_data(citycode)
        if dailytraffic_iter is None:
            return
        mapping = dict()  # 存放需要缓存的数据
        insert_values_list = list()  # 存放插入数据库的数据
        flag = 0  # 用来分割昨天和现在 的数据
        for dailytraffic in dailytraffic_iter:
            if dailytraffic.detailtime == "00:00:00":  # 将昨天的数据清除掉
                flag = 1

            elif flag == 0:
                continue
            insert_values_list.append(str((citycode, dailytraffic.date, dailytraffic.detailtime, dailytraffic.index)))
            mapping[dailytraffic.detailtime] = dailytraffic.index
        if not mapping:
            return
        #  缓存追加
        self.redis_worke.hash_value_append(key, mapping)
        self.redis_worke.expire(key, time_interval)
        # 插入mysql数据库

        values = ','.join(insert_values_list)
        sql = "insert into  digitalsmart.citytraffic(pid, ddate, ttime, rate)" \
              " values {data} ".format(data=values)
        self.mysql_worke.sumbit(sql)
