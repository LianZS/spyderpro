import datetime
import time
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

    def type_airstatus_check(self, now_time: datetime, time_difference: int):
        """

        :param now_time:
        :param time_difference:
        :return:
        """
        complete_keys_regular = "air:%d"
        search_regular = "air:*"
        sql = "select pid from digitalsmart.citymanager"
        complete_keys = self.get_complete_keys(sql, complete_keys_regular, search_regular)
        for key in complete_keys:
            # 获取缓存的数据
            lasttime = self._check_lasttime(key)
            # 检查数据是否完整
            if not lasttime:
                break
        # if self.time_difference(now_time, complete_keys) > time_difference or not check_status:
        #     result = self._check_airstatus_complete(complete_keys)
        #     return result
        # return True

    def _check_airstatus_complete(self, scence_type: int, time_interval: datetime.timedelta) -> bool:
        """

        :param scence_type:
        :param time_interval:
        :return:
        """

    def _complete_airstatus_data(self, key: str, pid: int, all_missing_time: dict):
        pass

    def _check_lasttime(self, key):
        lasttime = None
        redis_data = self.redis_worke.hash_get_all(key)
        for key in redis_data.keys():
            value = redis_data.get(key).decode()
            key = key.decode()
            if key == "lasttime":
                lasttime = value  # 格式2019-09-26 21:25:55.703345
        if lasttime is None:
            return None
        year, month, day, hour, minute, seconds = re.findall("(\d{4})-(\d{2})-(\d{2})\s(\d{2}):(\d{2}):(\d{2})",
                                                             lasttime)[0]


CompleteAirStatus().type_airstatus_check(datetime.datetime.now(), 200)
