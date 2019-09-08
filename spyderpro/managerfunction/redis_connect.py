import redis


def check_state(func):
    """
    检查连接池是否关闭
    :param func:
    :return:
    """

    def wrapper(self, *args, **kwargs):
        if self._shutdown:
            raise RuntimeError('连接池已经关闭，无法创建新的连接')
        return func(self, *args, **kwargs)

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

    def _init_pool_(self):
        """
        初始化连接池
        :return:
        """
        pool = redis.ConnectionPool(max_connections=self._max_workers)
        self._redis_pool = redis.Redis(connection_pool=pool)

    @check_state
    def expire(self, name, time_interval) -> int:

        """
        设置有效时间
        :param name: 键名
        :param time_interval: 有效时间
        :return:
        """

        result: int = self._redis_pool.expire(name, time_interval)
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
        resuslt: bool = self._redis_pool.set(name, value, ex=ex, px=px, nx=nx, xx=xx)
        return resuslt

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

        :param name:
        :param start:
        :param end:
        :return:
        """
        if isinstance(start, int) and isinstance(end, int):
            if start >= 0 and end >= 0 and start <= end:
                result = self._redis_pool.getrange(name, start, end)
            else:
                raise AttributeError("索引错误")
        else:
            result = self._redis_pool.get(name)
        return result

    @check_state
    def hashset(self, name, mapping) -> bool:

        result = self._redis_pool.hmset(name, mapping)
        return result

    def shutdown(self):
        self._shutdown = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


r = RedisConnectPool(max_workers=1)
r.set("name", "lian")
a = r.get("name")
print(a)
r.hashset("people", {"age": 2, "name": 'lian'})
