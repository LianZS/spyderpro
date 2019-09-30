import datetime
import time
import json
from typing import Iterator
from setting import *
from spyderpro.pool.threadpool import ThreadPool
from spyderpro.pool.mysql_connect import ConnectPool
from spyderpro.pool.redis_connect import RedisConnectPool
from spyderpro.function.people_function.posititioning_scence import ScenceFlow
from spyderpro.function.people_function.positioning_trend import PositioningTrend
from spyderpro.function.people_function.positioning_situation import PositioningSituation
from spyderpro.function.people_function.monitoring_area import PositioningPeople


class ManagerScence(PositioningPeople):
    """
    缓存数据格式
        景区人数： key= "scence:{0}:{1}".format(pid,type_flag),value={"HH:MM:SS":num,.....}
        人流趋势：key = "trend:{pid}".format(pid=region_id) ，value={'00:00:00':rate}
        人流分布： key = "distribution:{0}".format(pide)  value=str([{"lat": centerlat + item.latitude, "lng": centerlon + item.longitude,
                               "count": item.number},......)



    """

    def __init__(self):
        self._redis_worker = RedisConnectPool(max_workers=7)

    def __del__(self):
        del self._redis_worker

    def manager_scence_situation(self):
        """
        景区客流数据管理----半小时一轮

        """
        # 景区数据源类别--百度为1，腾讯为0
        type_flag = 1
        # 接连接池

        mysql_pool = ConnectPool(max_workers=6, host=host, user=user, password=password, port=port, database=database)
        # 获取需要获取实时客流量数据的景区信息
        sql = "select ds.pid,dt.table_id from digitalsmart.scencemanager as ds inner join digitalsmart.tablemanager " \
              "as dt on ds.type_flag=dt.flag   and ds.pid=dt.pid where ds.type_flag=1"
        # 提交mysql查询
        iterator_pids = mysql_pool.select(sql)
        # 线程池
        thread_pool = ThreadPool(max_workers=6)
        ddate: int = int(str(datetime.datetime.today().date()).replace("-", ''))

        # 缓存时间
        time_interval = datetime.timedelta(minutes=33)
        scence = ScenceFlow()
        # 开始请求
        for pid, table_id in iterator_pids:
            def fast(area_id, table_index):
                """
                请求景区客流量数据以及写入数据库和内存
                :param area_id: 景区id
                :param table_index: 景区所处表序号
                :return:
                """
                # 获取最新的客流量数据
                positioning_instances = scence.get_scence_situation(area_id)
                # 过滤重复的数据后的定位人流数据
                filter_positioning_instances = iter(scence.filter_peopleflow(mysql_pool, positioning_instances, ddate,
                                                                             area_id,
                                                                             table_index))

                # 缓存人流定位数据
                cache_data_mapping = dict()
                for positioning in positioning_instances:
                    cache_data_mapping[positioning.detailTime] = positioning.num
                # 缓存key
                redis_key = "scence:{0}:{1}".format(area_id, type_flag)

                # 缓存
                self._redis_worker.hashset(name=redis_key, mapping=cache_data_mapping)
                self._redis_worker.expire(name=redis_key, time_interval=time_interval)

                # 确定插入哪张表
                sql_format = "insert into digitalsmart.historyscenceflow{table_index} (pid, ddate, ttime, num) " \
                             "values ('%d','%d','%s','%d')".format(table_index=table_index)
                # 开始插入mysql数据库
                for positioning in filter_positioning_instances:
                    sql_cmd = sql_format % (
                        positioning.region_id, positioning.date, positioning.detailTime, positioning.num)
                    # 提交
                    mysql_pool.sumbit(sql_cmd)

            # 提交任务
            thread_pool.submit(fast, pid, table_id)
        # 开始执行任务队列
        thread_pool.run()
        # 关闭线程池
        thread_pool.close()
        # 关闭mysql连接池
        mysql_pool.close()

        print("百度资源景区数据挖掘完毕")

    def manager_scence_trend(self):
        """
        地区人口趋势数据管理---5分钟一次
        :return:
        """
        # 今天
        date_today = datetime.datetime.today()
        # 时间间隔
        time_inv = datetime.timedelta(days=1)
        # 明天
        date_tomorrow = date_today + time_inv
        # 今天日期
        str_start = str(date_today.date())

        # 结束日期
        str_end = str(date_tomorrow.date())
        # mysql 连接池
        mysql_pool = ConnectPool(max_workers=6, host=host, user=user, password=password, port=port, database=database)
        # 查询需要获取客流量趋势的景区信息
        sql = "select pid,area from digitalsmart.scencemanager where type_flag=0 "
        # 提交查询请求
        data = mysql_pool.select(sql)
        # 连接线程池
        thread_pool = ThreadPool(max_workers=6)
        # 缓存时间
        time_interval = datetime.timedelta(minutes=33)
        pos_trend = PositioningTrend()
        # 更新数据
        for item in data:
            # 景区唯一标识
            pid = item[0]
            # 景区名字
            area = item[1]

            def fast(region_id, place):
                """
                请求景区客流量趋势，写入数据库以及内存
                :param region_id:景区标识
                :param place: 景区名
                :return:
                """
                # 景区数据最近的更新时间
                sql_cmd = "select ttime from digitalsmart.scencetrend where pid={0} and ddate='{1}' " \
                          "order by ttime".format(region_id, int(str_start.replace("-", "")))
                # 默认-1点，当为-1时表示目前没有当天的任何数据
                last_ttime: str = "-1:00:00"

                try:
                    # 提交查询请求获取最近记录的时间
                    table_last_time = mysql_pool.select(sql_cmd)[-1][0]
                    last_ttime = str(table_last_time)
                except IndexError:
                    pass
                # 获取趋势数据
                trend_instances = pos_trend.get_place_index(name=place, placeid=region_id, date_start=str_start,
                                                            date_end=str_end)
                # 用来缓存数据
                cache_data_mapping = dict()
                # 插入数据以及缓存
                for trend in trend_instances:
                    ttime = trend.detailtime  # 该时间点
                    rate = trend.index  # 该时间点指数

                    cache_data_mapping[ttime] = rate
                    if ttime <= last_ttime:  # 过滤最近记录时间前的数据
                        continue

                    region_id = trend.region_id  # 景区标识
                    ddate = trend.ddate  # 目前日期
                    sql_cmd = "insert into digitalsmart.scencetrend(pid, ddate, ttime, rate) VALUE(%d,%d,'%s',%f)" % (
                        region_id, ddate, ttime, rate)
                    mysql_pool.sumbit(sql_cmd)  # 写入数据库
                # 缓存key
                if not cache_data_mapping:
                    return
                redis_key = "trend:{pid}".format(pid=region_id)
                # 缓存数据
                self._redis_worker.hashset(name=redis_key, mapping=cache_data_mapping)
                self._redis_worker.expire(name=redis_key, time_interval=time_interval)

            # 提交任务
            thread_pool.submit(fast, pid, area)
        # 执行任务队列
        thread_pool.run()
        # 关闭线程池
        thread_pool.close()
        # 关闭mysql连接池
        mysql_pool.close()

        print("景区趋势挖掘完毕")

    def manager_scenece_people(self):
        """
        更新某时刻的人流数据
        :return:
        """
        # mysql连接池
        self.mysql_pool = ConnectPool(max_workers=8, host=host, user=user, password=password, port=port,
                                      database=database)
        # 获取当前时间戳
        up_date = int(datetime.datetime.now().timestamp())
        # 查询需要查询的景区信息
        sql: str = "select pid,latitude,longitude from digitalsmart.scencemanager where type_flag=0"

        data = self.mysql_pool.select(sql)
        # 今天日期
        date_today = datetime.datetime.today()
        ddate = str(date_today.date())
        # 今天时间戳
        tmp_date = date_today.timestamp()
        if date_today.time().minute % 5 > 0:  # 纠正计算挤时间，分钟必须事5的倍数
            # 当前时间点
            now_time = date_today.time()
            # 调整当前时间点的分钟
            minute = now_time.minute - now_time.minute % 5
            detailtime = "{0:0>2}:{1:0>2}:00".format(now_time.hour, minute)
        else:
            detailtime = time.strftime("%H:%M:00", time.localtime(tmp_date))
        # 开启线程池
        thread_pool = ThreadPool(max_workers=6)
        pos = PositioningSituation()
        # 更新数据
        for info in data:  #

            def fast(item):
                """
                请求景区客流量趋势，写入数据库以及内存

                :param item: 景区基本信息字典
                :return:
                """
                region_id = item[0]  # 景区标识
                float_lat = item[1]  # 景区纬度
                float_lon = item[2]  # 景区经度

                # 判断数据对应在哪张表插入
                sql_cmd = "select table_id from digitalsmart.tablemanager where pid={0}".format(region_id)

                table_id = self.mysql_pool.select(sql_cmd)[0][0]
                # 请求最新的人流分布数据
                last_positioning_data = pos.get_scenece_people_json_data(date=ddate, dateTime=detailtime,
                                                                         region_id=region_id)
                if not last_positioning_data:  # 请求失败
                    return
                # 更新人流分布情况数据
                self.manager_scenece_people_distribution(last_positioning_data, region_id, up_date, float_lat,
                                                         float_lon, table_id)
                # Thread(target=self.manager_scenece_people_distribution,
                #        args=(last_positioning_data, region_id, up_date, float_lat, float_lon, table_id)).start()
                # 更新客流量数据
                self.manager_scenece_people_situation(table_id, last_positioning_data, region_id, ddate, detailtime)

            # 提交任务
            thread_pool.submit(fast, info)
        # 执行任务队列
        thread_pool.run()
        # 关闭线程池
        thread_pool.close()
        self.mysql_pool.close()
        print("景区人流数据挖掘完毕")

    def manager_scenece_people_distribution(self, scence_people_data: dict, region_id, tmp_date: int, centerlat: float,
                                            centerlon: float,
                                            table_id: int):
        """
         更新地区人口分布数据---这部分每次有几k条数据插入
        :param scence_people_data: 人流数据包
        :param region_id: 景区标识
        :param tmp_date: 时间戳
        :param centerlat: 中心纬度
        :param centerlon: 中心经度
        :param table_id: 表序号
        :return:
        """
        # scence_people_data中{',': 0}这类数据属于异常数据
        if len(scence_people_data.keys()) <= 1:
            return
        pos = PositioningSituation()
        # 获取经纬度人数结构体迭代器
        geographi_instances = pos.get_scence_distribution_situation(scence_people_data)
        # 确定哪张表
        select_table: str = "insert into digitalsmart.peopleposition{table_id} (pid, tmp_date, lat, lon, num) VALUES" \
            .format(table_id=table_id)
        # 存放经纬度人数数据
        geographi_instances = list(geographi_instances)
        # 需要插入数据库的数据生成器
        insert_mysql_geographi_datapack = self._generator_of_mysql_insert_data(geographi_instances, region_id, tmp_date,
                                                                               centerlat,
                                                                               centerlon)
        # 需要缓存的数据包生成器
        redis_data = self._generator_of_redis_insert_data(geographi_instances, centerlat, centerlon)

        # 缓存时间
        time_interval = datetime.timedelta(minutes=60)
        # 缓存key
        redis_key = "distribution:{0}".format(region_id)
        # 缓存数据
        try:
            value = json.dumps(list(redis_data))
        except Exception as e:
            print("列表序列化失败", e, region_id)
            return
            # 缓存
        self._redis_worker.set(name=redis_key, value=value)
        self._redis_worker.expire(name=redis_key, time_interval=time_interval)
        # 一条条提交到话会话很多时间在日志生成上，占用太多IO了，拼接起来再写入，只用一次日志时间而已
        # 但是需要注意的是，一次性不能拼接太多，管道大小有限制---需要在MySQL中增大Max_allowed_packet，否则会报错
        count = 0  # 用来计数
        geographi_data = list()  # 存放需要写入数据库的数据
        for geographi in insert_mysql_geographi_datapack:
            count += 1
            geographi_data.append(geographi)
            if count % 3000 == 0:
                sql_value = ','.join(geographi_data)
                sql = select_table + sql_value
                # 提交数据
                self.mysql_pool.sumbit(sql)
                geographi_data.clear()
        if len(geographi_data) > 0:
            sql_value = ','.join(geographi_data)

            sql = select_table + sql_value
            self.mysql_pool.sumbit(sql)

        # 更新人流分布管理表的修改时间
        sql = "update digitalsmart.tablemanager  " \
              "set last_date={0} where pid={1};".format(tmp_date, region_id)
        self.mysql_pool.sumbit(sql)

    def manager_scenece_people_situation(self, table_id: int, scence_people_data: dict, pid: int, ddate: str,
                                         ttime: str):
        """
        更新地区人口情况数据  ---这部分每次只有一条数据插入
        :param table_id: 表序号
        :param scence_people_data:人流数据包
        :param pid: 景区标识
        :param ddate: 日期：格式yyyy-mm-dd
        :param ttime: 时间，格式HH:MM:SS
        :return:
        """

        type_flag = 0  # 景区数据源类别--百度为1，腾讯为0
        pos = PositioningSituation()
        positioning_instance = pos.get_scence_people_count(scence_people_data, ddate, ttime, pid)
        sql_format = "insert into digitalsmart.historyscenceflow{table_id}(pid, ddate, ttime, num) values (%d,%d,'%s',%d) ".format(
            table_id=table_id)

        sql = sql_format % (
            positioning_instance.region_id, positioning_instance.date, positioning_instance.detailTime,
            positioning_instance.num)
        # 插入mysql数据库
        self.mysql_pool.sumbit(sql)
        format_int_of_ddate = int(ddate.replace("-", ''))
        sql = "select ttime,num from digitalsmart.historyscenceflow{table_id} where ddate={ddate};".format(
            table_id=table_id, ddate=format_int_of_ddate)
        # 需要缓存的数据
        people_flow_data = self.mysql_pool.select(sql)
        cache_data_mapping = dict()
        for people_flow in people_flow_data:
            ttime = people_flow[0]  # 时间
            num = people_flow[1]  # 客流数
            cache_data_mapping[str(ttime)] = num
        # 缓存时间
        if not cache_data_mapping:
            return
        time_interval = datetime.timedelta(minutes=60)
        # 缓存key
        redis_key = "scence:{0}:{1}".format(pid, type_flag)
        # 缓存
        self._redis_worker.hashset(name=redis_key, mapping=cache_data_mapping)
        self._redis_worker.expire(name=redis_key, time_interval=time_interval)

    @staticmethod
    def _generator_of_mysql_insert_data(source_data: list, region_id: int, tmp_date: int, centerlat: float,
                                        centerlon: float) -> Iterator[str]:
        """
        生产需要插入数据库的景区人流分布数据生成器
        :param source_data: 对象数据包
        :param region_id: 景区标识
        :param tmp_date: 时间戳
        :param centerlat: 中心纬度
        :param centerlon: 中心经度
        :return:
        """
        for instance in source_data:
            yield str((region_id, tmp_date, centerlat + instance.latitude, centerlon + instance.longitude,
                       instance.number))

    @staticmethod
    def _generator_of_redis_insert_data(source_data: list, centerlat: float, centerlon: float):
        """
        生成需要缓存再redis里的生成器
        :param source_data: 对象数据包
        :param centerlat: 中心纬度
        :param centerlon: 中心经度
        :return:
        """
        for instance in source_data:
            yield {"lat": centerlat + instance.latitude, "lng": centerlon + instance.longitude,
                   "count": instance.number}


if __name__ == "__main__":
    from multiprocessing import Process

    m = ManagerScence()
    Process(target=m.manager_scence_trend).start()
    Process(target=m.manager_scence_situation).start()
    Process(target=m.manager_scenece_people).start()
