import datetime
import re
from spyderpro.data_requests.weather.airstate import AirState
from spyderpro.complete_data._complete_data_interface import CompleteDataInterface


class CompleteAirStatus(CompleteDataInterface):
    """
        空气缓存数据补全
        空气质量 key = "air:{0}".format(pid)
        value = {"pid": pid, "aqi": aqi, "pm2": pm2, "pm10": pm10, "co": co, "no2": no2, "o3": o3, "so2": so2,
                         "flag": 1, "lasttime": str(now)}
    """

    def type_airstatus_check(self, now_time: datetime, time_interval: datetime.timedelta, time_difference: int):
        """
        检查空气质量数据并补全
        :param now_time: 此时时间
        :param time_interval: 缓存时间
        :param time_difference: 允许的超时时长
        :return:
        """
        complete_keys_regular = "air:%d"
        search_regular = "air:*"
        sql = "select pid from digitalsmart.citymanager"
        complete_keys = self.get_complete_keys(sql, complete_keys_regular, search_regular)
        lasttime = None
        for key in complete_keys:
            # 获取缓存的数据
            lasttime = self._check_lasttime(key)
            # 检查数据是否完整

            if not lasttime:
                self._check_airstatus_complete(complete_keys, time_interval, now_time)
                return
        # 之前数据更新时间与现在的时间差
        timedelta = (now_time - lasttime).seconds
        if timedelta > time_difference:
            self._check_airstatus_complete(complete_keys, time_interval, now_time)

        return True

    def _check_airstatus_complete(self, complete_keys: list, time_interval: datetime.timedelta,
                                  now_time: datetime.datetime) -> bool:
        """
        提交补全空气质量数据请求
        :param complete_keys:缓存keys
        :param time_interval:缓存时间
        :param now_time:此时时间
        :return:
        """

        air = AirState()
        # 获取城市空气数据pid
        info_airpid_obj = air.get_city_air_pid()
        city_air_map = dict()  # 存放城市空气pid
        for airobj in info_airpid_obj:
            city_air_map[airobj.city] = airobj.aqi_pid
        sql = "select pid,name from digitalsmart.citymanager"
        city_info = self.mysql_worke.select(sql)
        citypid_key_map = dict()  # 存放城市pid与缓存key关系
        for key in complete_keys:
            pid = re.match("air:(\d+)", key).group(1)
            citypid_key_map[pid] = key
        # 请求补全数据
        for citypid, city_name in city_info:
            redis_key = citypid_key_map[str(citypid)]
            city_weather_pid = city_air_map[city_name]
            self._complete_airstatus_data(redis_key, citypid, city_weather_pid, time_interval, now_time)
        sql = "select lasttime from digitalsmart.airstate where flag=1"
        try:
            lasttime = self.mysql_worke.select(sql)[0][0]  # 最近更新时间
        except TypeError:
            lasttime = None
        if lasttime:
            # 更新数据库有效数据
            sql = "update digitalsmart.airstate set flag=0 where lasttime='{0}'".format(lasttime)
            self.mysql_worke.sumbit(sql)
        return True

    def _complete_airstatus_data(self, key: str, city_pid: int, city_weather_pid: int,
                                 time_interval: datetime.timedelta, now_time: datetime.datetime):
        """
        补全空气中质量数据
        :param key:缓存key
        :param city_pid:城市表示
        :param city_weather_pid:城市天气pid表示
        :param time_interval:缓存时间
        :param now_time:此时时间
        :return:
        """
        air = AirState()
        # 请求天气数据
        aqi_state = air.get_city_air_state(city_weather_pid)

        aqi = aqi_state.aqi
        pm2 = aqi_state.pm2
        pm10 = aqi_state.pm10
        so2 = aqi_state.so2
        no2 = aqi_state.no2
        co = aqi_state.co
        o3 = aqi_state.o3
        # 缓存数据
        value = {"pid": city_pid, "aqi": aqi, "pm2": pm2, "pm10": pm10, "co": co, "no2": no2, "o3": o3, "so2": so2,
                 "flag": 1, "lasttime": str(now_time)}
        self.redis_worke.hashset(key, value)
        self.redis_worke.expire(name=key, time_interval=time_interval)
        # 更新数据库
        sql = "insert into digitalsmart.airstate(pid, aqi, pm2, pm10, co, no2, o3, so2, flag, lasttime) " \
              "value (%d,%d,%d,%d,%f,%d,%d,%d,%d,'%s')" % (city_pid, aqi, pm2, pm10, co, no2, o3, so2, 1, now_time)
        self.mysql_worke.sumbit(sql)

    def _check_lasttime(self, key):
        """
        获取最近数据的更新时间
        :param key: 缓存key
        :return:
        """
        lasttime = None
        redis_data = self.redis_worke.hash_get_all(key)
        for key in redis_data.keys():
            value = redis_data.get(key).decode()
            key = key.decode()
            if key == "lasttime":  # 最近更新时间
                lasttime = value  # 格式2019-09-26 21:25:55.703345
        if lasttime is None:
            return None
        year, month, day, hour, minute, seconds = re.findall("(\d{4})-(\d{2})-(\d{2})\s(\d{2}):(\d{2}):(\d{2})",
                                                             lasttime)[0]
        # 最近更新时间
        update_lasttime = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(seconds))
        return update_lasttime
