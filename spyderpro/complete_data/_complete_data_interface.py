import datetime
import time
from typing import Iterator, List
from setting import *

from spyderpro.pool.redis_connect import RedisConnectPool
from spyderpro.pool.mysql_connect import ConnectPool


class CompleteDataInterface:
    """
    在使用redis的连接池访问redis里的资源时，连接池数必须大于等于并发数（二者同时小于redis可支持的最大连接数），
        否则多出来的并发数将会因为分配不到redis的资源而收到报错信息
    """

    def __init__(self):
        self.redis_worke = RedisConnectPool(max_workers=10)
        self.mysql_worke = ConnectPool(max_workers=1, host=host, user=user, password=password, port=port,
                                       database=database)

    def __del__(self):
        self.mysql_worke.close()
        del self.redis_worke
        del self.mysql_worke

    @staticmethod
    def check_keys_complete(source_keys: list, target_keys: list) -> List:
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

    @staticmethod
    def check_data_complete(source_data: list, time_interval: datetime.timedelta) -> bool:
        """
         检查数据的完整性
         :param source_data: 此处采用检查redis缓存的时间序列时间序列,格式HH:MM:SS
        :param time_interval: 时间序列的间隔
        :return:true表示数据完整
        """
        if len(source_data) == 0:
            return False
        now_time = datetime.datetime.now()
        temp_collection = list()
        for item in source_data:
            temp_collection.append(item.decode())
        source_data = temp_collection
        max_time = max(source_data)  # 最大的时间
        last_time = time.strptime(max_time, "%H:%M:%S")
        redis_last_time = datetime.datetime(now_time.year, now_time.month, now_time.day, last_time.tm_hour,
                                            last_time.tm_min,
                                            last_time.tm_sec)
        init_time = datetime.datetime(now_time.year, now_time.month, now_time.day, 0, 0, 0)  # 数据的起始时间
        standard_length = int(
            (redis_last_time.timestamp() - init_time.timestamp()) / time_interval.seconds) + 1  # 完整数据的长度
        if len(source_data) < standard_length:
            return False
        else:
            return True

    def get_mysql_complete_keys(self, sql, regular) -> Iterator:
        """
        获取mysql数据组合成完整的缓存keys
        :param sql: mysql查询语句
        :param regular: key模板
        :return:key
        """
        iter_pids = self.mysql_worke.select(sql)
        for pid in iter_pids:
            yield regular % pid

    def get_complete_keys(self, sql: str, complete_keys_regular: str, search_regular: str) -> List:
        """
        对比mysql组成的key和redis缓存的key产生最完整的keys
        :param sql:查询语句
        :param complete_keys_regular: mysql组合的缓存key模板
        :param search_regular: redis缓存的key模板
        :return:
        """

        # 获取mysql组合成的完整的keys
        source_complete_keys = self.get_mysql_complete_keys(sql, complete_keys_regular)

        # redis key扫描
        keys = self.redis_worke.get_keys(search_regular)
        target_keys = list()
        for key in keys:  # 解码
            key = key.decode()
            target_keys.append(key)
        # 检查keys是否完整,获得最完整的keys
        comple_keys = self.check_keys_complete(list(source_complete_keys), target_keys)
        return comple_keys

    def time_difference(self, now_time: datetime, complete_keys: list) -> int:
        """
        获取redis数据缓存时间中偏离现在的最长时间
        :param now_time: 此时
        :param complete_keys:redis缓存的keys
        :return:时间差
        """
        time_list = list()  # 存放缓存数据的key的最大时间
        for key in complete_keys:
            redis_data = self.redis_worke.hash_get_all(key)
            #  只要有出现了空数据，则需要调用检查
            if not redis_data:
                return 1000000
            max_time = max(redis_data.keys()).decode()
            time_list.append(max_time)

        min_time = min(time_list)
        last_time = time.strptime(min_time, "%H:%M:%S")
        redis_last_time = datetime.datetime(now_time.year, now_time.month, now_time.day, last_time.tm_hour,
                                            last_time.tm_min,
                                            last_time.tm_sec)
        time_inv = now_time.timestamp() - redis_last_time.timestamp()  # 时间差
        return time_inv
