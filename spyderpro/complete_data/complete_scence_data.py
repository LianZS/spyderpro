import datetime
from spyderpro.pool.redis_connect import RedisConnectPool
from spyderpro.data_requests.scence.place_people_num import PlacePeopleNum
from spyderpro.data_requests.scence.place_people_trend import PlaceTrend


class CompleteScenceData:
    def __init__(self):
        self._redis_work = RedisConnectPool(max_workers=1)

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

        today = datetime.datetime.today()
        today_ddate = str(today.date())
        place = PlacePeopleNum()
        for miss_time in missing_time.keys():
            # 请求热力图数据
            response_data = place.get_heatdata_bytime(ddate=today_ddate, date_time=miss_time, region_id=pid)
            if not response_data:
                continue
            # 统计数据
            positioning = place.count_headdata(response_data, today_ddate, miss_time, pid)
            # 缓存追加
            self._redis_work.hash_value_append(key, {positioning.detailTime: positioning.num})

    def complete_scence_people_trend_data(self, key: str, area_name: str, pid: int):
        """

        :param key: 缓存key
        :param area_name: 景区名
        :param pid: 景区标识
        :return:
        """
        now = datetime.datetime.today()
        time_interval = datetime.timedelta(days=1)
        tomorrow = now + time_interval
        today = str(now.date())
        tomorrow_day = str(tomorrow.date())

        trend = PlaceTrend(today, tomorrow_day)
        result_objs = trend.get_trend(area_name, pid)
        redis_data = dict()
        for obj in result_objs:
            redis_data[obj.detailtime] = obj.index
        self._redis_work.hashset(key, redis_data)
