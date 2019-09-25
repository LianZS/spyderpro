import datetime
import copy
from typing import Iterator, List
from spyderpro.pool.redis_connect import RedisConnectPool
from spyderpro.pool.mysql_connect import ConnectPool


class ManagerRAW:
    """
    内存数据管理
    """

    def __init__(self):
        self._redis_worke = RedisConnectPool(max_workers=10)
        self._mysql_worke = ConnectPool(max_workers=1)

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
        # 初始化一整天时间点列表
        init_time = datetime.datetime(2019, 1, 1, 0, 0, 0)  # 初始化时间，时间点以00：00：00为基准点
        now = datetime.datetime.now()
        now_time = str(now.time())
        time_interval = datetime.timedelta(minutes=5)  # 时间间隔
        complete_time = dict()  # 存放一整天的时间点

        while 1:
            complete_time[str(init_time.time())] = 0  # 键值0表示该时间点还没有数据，1表示有
            init_time = init_time + time_interval
            if str(init_time.time()) > now_time:
                break
        # 缓存key模板
        complete_keys_regular = "scence:%d:0"
        sql = "select pid from digitalsmart.scencemanager where type_flag=0"
        # 获取完整的key
        source_complete_keys = self._get_complete_keys(sql, complete_keys_regular)

        # 进行一类数据key扫描
        search_regular = "scence:*:0"
        keys = self._redis_worke.get_keys(search_regular)
        target_keys = list()
        for key in keys:  # 解码
            key = key.decode()
            target_keys.append(keys)

        # 检查keys是否完整,获得最完整的keys
        comple_keys = self._check_keys_complete(list(source_complete_keys), target_keys)
        for redis_key in comple_keys:
            temp_complete_time = copy.deepcopy(complete_time)
            result = self._redis_worke.hash_get_all(redis_key)
            for time_key in result.keys():
                time_key = time_key.decode()
                temp_complete_time.pop(time_key)  # pop已经存在的数据
            # 补全缺少的数据

    def _get_complete_keys(self, sql, regular) -> Iterator:
        """
        获取完整的keys
        :param sql: mysql查询语句
        :param regular: key模板
        :return:key
        """
        iter_pids = self._mysql_worke.select(sql)
        for pid in iter_pids:
            yield regular % pid

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

    def _check_keys_complete(self, source_keys: list, target_keys: list) -> List:
        """
        检查缓存key的完整性
        :param source_keys: 完整的keys
        :param target_keys: 需要的检查的keys
        :return:
        """
        if len(source_keys) == len(target_keys):
            # 检查是否完全正确
            for key in target_keys:
                result = source_keys.count(key)
                if result != 1:  # 有不正确的数据
                    return source_keys

            return target_keys
        else:

            return source_keys

    def _check_data_complete(self):
        """
        检查数据的完整性
        :return:
        """


ManagerRAW().check_scence_people_num_complete()