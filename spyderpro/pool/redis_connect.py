import redis
from threading import Semaphore


def check_state(func):
    """
    检查连接池是否关闭
    :param func:
    :return:
    """

    def wrapper(self, *args, **kwargs):
        if self._shutdown:
            raise RuntimeError('连接池已经关闭，无法创建新的连接')
        self._semaphore.acquire()
        result = func(self, *args, **kwargs)
        self._semaphore.release()

        return result

    return wrapper


class RedisConnectPool(object):
    _instance = None
    _bool_instance_flag = False
    _shutdown = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._bool_instance_flag = True
        return cls._instance

    def __init__(self, max_workers=None):

        if RedisConnectPool._bool_instance_flag:
            if max_workers is None:
                max_workers = 10
            if max_workers <= 0:
                raise ValueError("连接池必须大于0")
            self._max_workers = max_workers
            self._broken = False
            self._shutdown = False
            self._init_pool_()
            self._semaphore = Semaphore(10)  # 解决并发时too many connect 错误

    def _init_pool_(self):
        """
        初始化连接池
        :return:
        """

        pool = redis.ConnectionPool(max_connections=self._max_workers, host='localhost', port=6379)
        self._redis_pool = redis.Redis(connection_pool=pool)

    @check_state
    def expire(self, name, time_interval) -> int:

        """
        设置有效时间
        :param name: 键名
        :param time_interval: 有效时间
        :return:
        """
        pipe = self._redis_pool.pipeline()
        result: int = self._redis_pool.expire(name, time_interval)
        pipe.execute()

        return result

    @check_state
    def set(self, name, value, ex=None, px=None, nx=False, xx=False) -> bool:
        """
        String类型设置

        :param name: 键名
        :param value: 键值
        :param ex: 秒时间
        :param px: 毫秒时间
        :param nx:if set to True, set the value at key ``name`` to ``value`` only
            if it does not exist.
        :param xx:if set to True, set the value at key ``name`` to ``value`` only
            if it already exists.
        :return:
        """

        with self._redis_pool.pipeline() as pipe:
            try:

                pipe.watch(name)
                pipe.multi()
                resuslt: bool = pipe.set(name, value, ex=ex, px=px, nx=nx, xx=xx)
                pipe.execute()
                return resuslt

            except redis.exceptions.WatchError:
                print("%s --WatchError" % name)

    @check_state
    def ttl(self, name) -> int:
        """
        查看剩余有效期
        :param name: 键名
        :return:
        """

        result: int = self._redis_pool.ttl(name)
        return result

    @check_state
    def get(self, name: str, start: int = None, end: int = None):
        """

        :param name:键值
        :param start:起始索引
        :param end:结束索引
        :return:
        """

        if isinstance(start, int) and isinstance(end, int):

            if start >= 0 and start <= end:
                result = self._redis_pool.getrange(name, start, end)
            else:
                raise AttributeError("索引错误")
        else:
            result = self._redis_pool.get(name)

        return result

    @check_state
    def strlen(self, name) -> int:
        """
        redis String 值长度
        :param name: 键名
        :return:
        """

        length: int = self._redis_pool.strlen(name)
        return length

    @check_state
    def hashset(self, name, mapping: dict) -> bool:
        """
        哈希添加
        :param name:key
        :param mapping: 键值对
        :return:
        """
        with self._redis_pool.pipeline() as pipe:
            try:
                pipe.watch(name)
                pipe.multi()
                resuslt: bool = pipe.hmset(name, mapping)
                pipe.execute()
                return resuslt

            except redis.exceptions.WatchError:
                print("%s --WatchError" % name)

    @check_state
    def hash_value_append(self, name, mapping: dict) -> bool:
        """
        哈希增加
        :param name: key
        :param mapping: 追加的dict
        :return:
        """
        if len(mapping.keys()) == 0:
            return True

        with self._redis_pool.pipeline() as pipe:
            pipe.watch(name)
            pre_value = pipe.hgetall(name=name)  # 原先的数据
            for key, value in pre_value.items():
                key = key.decode("utf-8")
                value = value.decode("utf-8")
                mapping[key] = value
            pipe.multi()
            result = pipe.hmset(name, mapping)
            pipe.execute()

            return result

    @check_state
    def hashget(self, name, keys):
        """
        哈希查询
        :param name:
        :param keys:
        :return:
        """
        result = self._redis_pool.hmget(name=name, keys=keys)
        return result

    @check_state
    def hashkeys(self, name) -> list:
        """
        获取所有哈希keys
        :param name:
        :return:
        """
        result: list = self._redis_pool.hkeys(name)
        return result

    @check_state
    def hlen(self, name) -> int:
        """
        哈希长度
        :param name:
        :return:
        """
        length = self._redis_pool.hlen(name)
        return length

    @check_state
    def lpush(self, name, values: list) -> bool:
        """
        list左插入
        :param name:
        :param values:
        :return:
        """
        with self._redis_pool.pipeline() as pipe:
            try:

                pipe.watch(name)
                pipe.multi()
                resuslt: bool = pipe.lpush(name, *values)
                pipe.execute()
                return resuslt

            except redis.exceptions.WatchError:
                print("%s --WatchError" % name)

    @check_state
    def rpush(self, name, values: list) -> bool:
        """
        list右插入
        :param name:
        :param values:
        :return:
        """
        with self._redis_pool.pipeline() as pipe:
            try:

                pipe.watch(name)
                pipe.multi()
                resuslt: bool = pipe.rpush(name, *values)
                pipe.execute()
                return resuslt

            except redis.exceptions.WatchError:
                print("%s --WatchError" % name)

    @check_state
    def lrange(self, name, start, end) -> list:
        """
        list左查询
        :param name:
        :param start:
        :param end:
        :return:
        """
        max_len = self.llen(name)
        if end > max_len:
            raise AttributeError("索引值过大")
        result: list = self._redis_pool.lrange(name, start, end)
        return result

    @check_state
    def llen(self, name):
        """
        list长度
        :param name:
        :return:
        """
        result: int = self._redis_pool.llen(name)
        return result

    @check_state
    def zset(self, name, mapping: dict):
        """
        set添加
        :param name:
        :param mapping: 键值对
        :return:
        """
        with self._redis_pool.pipeline() as pipe:
            try:

                pipe.watch(name)
                pipe.multi()
                resuslt: bool = pipe.zadd(name, mapping)
                pipe.execute()
                return resuslt

            except redis.exceptions.WatchError:
                print("%s --WatchError" % name)

    @check_state
    def zlen(self, name) -> int:
        """
        set长度
        :param name:
        :return:
        """
        length: int = self._redis_pool.zcard(name)
        return length

    def zrange_members(self, name) -> list:
        """
        获取zset里面的所有元素
        :param name:
        :return:
        """
        length = self._redis_pool.zcard(name)
        result: list = self._redis_pool.zrange(name, 0, length, withscores=True)
        return result

    def shutdown(self):
        """
        关闭连接池
        :return:
        """
        self._shutdown = True

    def __del__(self):
        self._redis_pool.connection_pool.disconnect()
