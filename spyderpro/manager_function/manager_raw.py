import datetime
from multiprocessing import Process
from spyderpro.complete_data.complete_scence_data import CompleteScenceData
from spyderpro.complete_data.complete_traffic_data import CompleteTraffic
from spyderpro.complete_data.complete_airstatus_data import CompleteAirStatus


class ManagerRAW:
    """
    内存数据管理
    """

    def __init__(self):
        pass

    @staticmethod
    def manager_scence_data_raw():
        """
        管理景区缓存数据，确保数据完整性,
        各类缓存key格式：
         景区人数： key= "scence:{0}:{1}".format(pid,type_flag),value={"HH:MM:SS":num,.....}
        人流趋势：key = "trend:{pid}".format(pid=region_id) ，value={'00:00:00':rate}
        人流分布： key = "distribution:{0}".format(pide)  value=str([{"lat": centerlat + item.latitude,
                                                                    "lng": centerlon + item.longitude,
                               "count": item.number},......)

        """
        complete = CompleteScenceData()
        now_time = datetime.datetime.now()
        cache_time = datetime.timedelta(minutes=60)  # 数据缓存时间
        time_interval = datetime.timedelta(minutes=30)  # 缓存数据的时间间隔

        # 检查第二类景区--数据间隔30分钟
        complete.type_scence_people_num_check(1, now_time, cache_time, time_interval, 3600)
        time_interval = datetime.timedelta(minutes=5)  # 缓存数据的时间间隔
        # 检查一类景区人流趋势是否完整
        complete.type_scence_people_trend_check(now_time, cache_time, time_interval, 2100)
        exit()
        # 下面检查第一类景区---数据间隔5分钟
        complete.type_scence_people_num_check(0, now_time, cache_time, time_interval, 2100)

    @staticmethod
    def manager_citytraffic_data_raw():
        """
        管理交通缓存数据，确保数据完整性,
        日常交通拥堵延迟指数：key= "traffic:{0}".format(region_id),mapping ={"HH:MM:SS":rate,....}
        道路交通数据：key ="road:{pid}:{road_id}".format(pid=region_id, road_id=roadid)
                        value =str( {
                            "pid": pid, "roadname": roadname, "up_date": up_date, "speed": speed,
                            "direction": direction, "bounds": bound, "data": data,
                            "roadpid": roadid, "rate": rate
                        })
        季度交通数据：key = "yeartraffic:{pid}".format(pid=region_id) ,value={'yyyymmdd':rate,....}
        :return:
        """
        complete = CompleteTraffic()
        now_time = datetime.datetime.now()
        cache_time = datetime.timedelta(minutes=60)  # 数据缓存时间

        # 检查一类城市交通延迟数据是否完整
        time_interval = datetime.timedelta(minutes=5)  # 时间间隔
        complete.type_daily_citytraffic_check(0, now_time, cache_time, time_interval, 2100)
        # 检查第二类城市交通--数据间隔30分钟
        time_interval = datetime.timedelta(minutes=60)  # 时间间隔
        complete.type_daily_citytraffic_check(1, now_time, cache_time, time_interval, 3 * 3600)

    @staticmethod
    def manager_airstatus_data_raw():
        """
        管理空气缓存数据，确保数据完整性,
        各类缓存key格式：
           空气质量 key = "air:{0}".format(pid)
            value = {"pid": pid, "aqi": aqi, "pm2": pm2, "pm10": pm10, "co": co, "no2": no2, "o3": o3, "so2": so2,
                         "flag": 1, "lasttime": str(now)}
        :return:
        """
        complete = CompleteAirStatus()
        now_time = datetime.datetime.now()
        cache_time = datetime.timedelta(minutes=60)  # 数据缓存时间
        complete.type_airstatus_check(now_time, cache_time, 2 * 3600)


