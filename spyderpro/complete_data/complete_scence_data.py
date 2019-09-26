import datetime
from threading import Lock
from spyderpro.pool.redis_connect import RedisConnectPool
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

    def __del__(self):
        del self._redis_work

    def complete_scence_people_num_data(self, key: str, pid: int, missing_time: dict):
        """
        补全缺失的数据
        :param key: 缓存key
        :param missing_time:缺失数据的时间点
        :param pid:景区标识
        :return:
        """
        time_interval = datetime.timedelta(minutes=60)
        pool = ThreadPool(max_workers=10)
        for miss_time in missing_time.keys():
            pool.submit(self._fast, pid, miss_time)
        pool.run()
        pool.close()
        mapping = dict()  # 存放需要缓存的数据

        # 并发返回结果
        for positioning in pool.result:
            mapping[positioning.detailTime] = positioning.num
        #  缓存追加
        self._redis_work.hash_value_append(key, mapping)
        self._redis_work.expire(key, time_interval)

    def _fast(self, pid: int, miss_time: str):
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
        for obj in result_objs:
            redis_data[obj.detailtime] = obj.index
        # 缓存
        self._redis_work.hashset(key, redis_data)
        self._redis_work.expire(key, redis_time)
