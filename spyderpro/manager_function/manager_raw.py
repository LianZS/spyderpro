import datetime
from spyderpro.complete_data.complete_scence_data import CompleteScenceData
from spyderpro.complete_data.complete_traffic_data import CompleteTraffic


class ManagerRAW:
    """
    内存数据管理
    """

    def __init__(self):
        pass

    def manager_scence_data_raw(self):
        """
        管理景区缓存数据，确保数据完整性,
        各类缓存key格式：
         景区人数： key= "scence:{0}:{1}".format(pid,type_flag),value={"HH:MM:SS":num,.....}
        人流趋势：key = "trend:{pid}".format(pid=region_id) ，value={'00:00:00':rate}
        人流分布： key = "distribution:{0}".format(pide)  value=str([{"lat": centerlat + item.latitude, "lng": centerlon + item.longitude,
                               "count": item.number},......)

        """
        complete = CompleteScenceData()
        now_time = datetime.datetime.now()
        # 检查人流趋势是否完整
        complete.type_scence_people_trend_check(now_time, 2100)
        # 下面检查第一类景区---数据间隔5分钟
        time_interval = datetime.timedelta(minutes=5)  # 时间间隔
        complete.type_scence_people_num_check(0, now_time, time_interval, 2100)
        # 检查第二类景区--数据间隔30分钟
        time_interval = datetime.timedelta(minutes=30)  # 时间间隔
        complete.type_scence_people_num_check(1, now_time, time_interval, 3600)

    def manager_citytraffic_data_raw(self):
        complete = CompleteTraffic()
        now_time = datetime.datetime.now()
        # 检查一类城市交通延迟数据是否完整
        time_interval = datetime.timedelta(minutes=5)  # 时间间隔
        complete.type_daily_citytraffic_check(0, now_time, time_interval, 2100)
        # 检查第二类城市交通--数据间隔30分钟
        time_interval = datetime.timedelta(minutes=30)  # 时间间隔
        complete.type_daily_citytraffic_check(1, now_time, time_interval, 3600)

