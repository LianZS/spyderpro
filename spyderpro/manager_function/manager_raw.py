from spyderpro.pool.redis_connect import RedisConnectPool


class ManagerRAW:
    """
    内存数据管理
    """

    def __init__(self):
        self._redis_worke = RedisConnectPool(max_workers=10)

    def __del__(self):
        del self._redis_worke

    def manager_scence_data_raw(self):
        """
        管理景区缓存数据，确保数据完整性,
        各类缓存key格式：
         景区人数： key= "scence:{0}:{1}".format(pid,type_flag),value={"HH:MM:SS":num,.....}
        人流趋势：key = "trend:{pid}".format(pid=region_id) ，value={'00:00:00':rate}
        人流分布： key = "distribution:{0}".format(pide)  value=str([{"lat": centerlat + item.latitude, "lng": centerlon + item.longitude,
                               "count": item.number},......)

        """

    def check_scence_people_num_complete(self):
        """
        检查景区人数数据的完整性
        :return:
        """

    def check_scence_people_trend_complete(self):
        """
        检查景区人数趋势的完整性
        :return:
        """

    def check_scence_people_distribution_complete(self):
        """
        检查景区人流分布的完整性
        :return:
        """

    def _check_keys_complete(self):
        """
        检查缓存key的完整性
        :return:
        """

    def _check_data_complete(self):
        """
        检查数据的完整性
        :return:
        """
