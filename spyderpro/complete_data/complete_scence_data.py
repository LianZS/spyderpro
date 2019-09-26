import datetime
from spyderpro.pool.redis_connect import RedisConnectPool
from spyderpro.pool.mysql_connect import ConnectPool
from spyderpro.data_requests.scence.place_people_num import PlacePeopleNum
from spyderpro.data_requests.scence.place_people_trend import PlaceTrend
from spyderpro.pool.threadpool import ThreadPool


class CompleteScenceData:
    def __init__(self):
        """
        在使用redis的连接池访问redis里的资源时，连接池数必须大于等于并发数（二者同时小于redis可支持的最大连接数），
        否则多出来的并发数将会因为分配不到redis的资源而收到报错信息
        """
        self._redis_work = RedisConnectPool(max_workers=10)
        self._mysql_work = ConnectPool(max_workers=1)

    def __del__(self):
        del self._redis_work

    def complete_scence_people_num_data(self, key: str, pid: int, all_missing_time: dict):
        """
        补全缺失的数据
        :param key: 缓存key
        :param missing_time:缺失数据的时间点
        :param pid:景区标识
        :return:
        """
        if len(all_missing_time) == 0:
            return
        time_interval = datetime.timedelta(minutes=60)
        pool = ThreadPool(max_workers=10)
        for miss_time in all_missing_time.keys():
            pool.submit(self._fast, pid, miss_time)
        pool.run()
        pool.close()
        mapping = dict()  # 存放需要缓存的数据
        # 判断数据对应在哪张表插入
        sql_cmd = "select table_id from digitalsmart.tablemanager where pid={0}".format(pid)
        table_id = self._mysql_work.select(sql_cmd)[0][0]
        # 插入数据库格式语句
        sql_format = "insert into digitalsmart.historyscenceflow{table_id} (pid, ddate, ttime, num) values ".format(
            table_id=table_id)
        insert_values_list = list()  # 存放插入数据库的数据
        # 并发返回结果
        for positioning in pool.result:
            insert_values_list.append(str((pid, positioning.date, positioning.detailTime, positioning.num)))
            mapping[positioning.detailTime] = positioning.num
        #  缓存追加
        self._redis_work.hash_value_append(key, mapping)
        self._redis_work.expire(key, time_interval)
        # 插入mysql数据库

        values = ','.join(insert_values_list)
        sql = sql_format + values
        self._mysql_work.sumbit(sql)

    @staticmethod
    def _fast(pid: int, miss_time: str):
        today = datetime.datetime.today()
        today_ddate = str(today.date())
        place = PlacePeopleNum()
        response_data = place.get_heatdata_bytime(ddate=today_ddate, date_time=miss_time, region_id=pid)
        if not response_data:
            return
        # 统计数据
        positioning = place.count_headdata(response_data, today_ddate, miss_time, pid)
        return positioning

    def complete_scence_people_trend_data(self, key: str, area_name: str, pid: int):
        """
         补全数据，这里直接将之前所有的数据写入
        :param key: 缓存key
        :param area_name: 景区名
        :param pid: 景区标识
        :return:
        """
        # 缓存时间
        redis_time = datetime.timedelta(minutes=60)
        now = datetime.datetime.today()  # 现在时间
        time_interval = datetime.timedelta(days=1)  # 时间间隔
        tomorrow = now + time_interval  # 明天
        today = str(now.date())
        tomorrow_day = str(tomorrow.date())
        trend = PlaceTrend(today, tomorrow_day)
        # 获取这天的趋势数据
        result_objs = trend.get_trend(area_name, pid)
        redis_data = dict()
        insert_values_list: list = list()  # 存放插入数据库的数据
        for obj in result_objs:
            insert_values_list.append(str((pid, obj.ddate, obj.detailtime, obj.index)))
            redis_data[obj.detailtime] = obj.index
        # 缓存
        self._redis_work.hashset(key, redis_data)
        self._redis_work.expire(key, redis_time)
        # 插入数据库
        values = ','.join(insert_values_list)
        sql = "insert into digitalsmart.scencetrend (pid, ddate, ttime, rate) VALUES {data}".format(data=values)
        self._mysql_work.sumbit(sql)
