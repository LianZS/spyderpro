from setting import *
from queue import Queue
from threading import Lock, Thread
from spyderpro.pool.connect_interface import ConnectInterface


class ConnectPool(ConnectInterface):
    _instance = None
    _bool_instance_flag = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._bool_instance_flag = True
        return cls._instance

    def __init__(self, max_workers, host, user, password, database,
                 port, connect_timeout=360):
        """

        :param max_workers: 最大连接数
        :param host:
        :param user:
        :param password:
        :param database:
        :param port:
        :param connect_timeout:
        """

        if ConnectPool._bool_instance_flag:
            self._lock = Lock()
            self._max_workers = max_workers
            self.work_queue = Queue(max_workers)
            self._broken = False
            self._shutdown = False
            self.select_connect = pymysql.connect(host=host, user=user, password=password, database=database,
                                                  port=port, connect_timeout=connect_timeout)  # 专门用来处理查询操作
            self._stop = Queue(max_workers)  # 通知连接池里的所有连接关闭
            self._init_pool_(host, user, password, database, port, connect_timeout)
            ConnectPool._bool_instance_flag = False

    def _init_pool_(self, host, user, password, database, port, connect_timeout):
        """
        初始化连接池
        :param host:
        :param user:
        :param password:
        :param database:
        :param port:
        :param connect_timeout:
        :return:
        """
        for i in range(self._max_workers):
            Thread(target=self.connect, args=(host, user, password, database,
                                              port, connect_timeout)).start()

    def connect(self, host, user, password, database,
                port, connect_timeout):
        db = pymysql.connect(host=host, user=user, password=password, database=database,
                             port=port, connect_timeout=connect_timeout)
        cur = db.cursor()
        while self._stop.get():
            sql = self.work_queue.get()  # 接受命令
            try:
                cur.execute(sql)
                db.commit()
            except Exception as e:
                print(e, sql)
                db.rollback()
        cur.close()
        db.close()

    def sumbit(self, sql_cmd: str):
        """
        插入, 删除，更新操作
        :param sql_cmd:sql语句
        :return:
        """
        if self._shutdown:
            raise RuntimeError('连接池已经关闭，无法创建新的连接')
        self._stop.put(1)
        self.work_queue.put(sql_cmd)

    def select(self, sql_cmd: str):
        """
        查询操作
        :param sql_cmd:sql语句
        :return:
        """
        if self._shutdown:
            raise RuntimeError('连接池已经关闭，无法创建新的连接')
        cur = self.select_connect.cursor()
        iterator_result = []
        try:
            self._lock.acquire()
            cur.execute(sql_cmd)
            iterator_result = cur.fetchall()
            self._lock.release()

        except Exception as e:
            print(e, sql_cmd)

        cur.close()

        return iterator_result

    def shutdown(self):
        self._shutdown = True

    def close(self):
        """
        关闭连接池所有连接
        :return:
        """

        for i in range(self._max_workers):
            self._stop.put(0)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.work_queue.empty()
