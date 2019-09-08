import redis
class RedisConnect(object):
    instance = None
    bool_instance_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.bool_instance_flag = True
        return cls.instance

    def __init__(self, max_workers=None):

        if ConnectPool.bool_instance_flag:
            if max_workers is None:
                max_workers = 10
            if max_workers <= 0:
                raise ValueError("连接池必须大于0")
            self._max_workers = max_workers
            self.work_queue = Queue(max_workers)
            self._broken = False
            self._shutdown = False
            self._init_pool_()

    def _init_pool_(self):
        """
        初始化连接池
        :return:
        """
        for i in range(self._max_workers):
            db = pymysql.connect(host=host, user=user, password=password, database='digitalsmart',
                                 port=port)
            self.work_queue.put(db)

    def sumbit(self, sql_cmd: str):
        """
        插入, 删除，更新操作
        :param sql_cmd:sql语句
        :return:
        """
        if self._shutdown:
            raise RuntimeError('连接池已经关闭，无法创建新的连接')

        db = self.work_queue.get()
        cur = db.cursor()
        try:

            cur.execute(sql_cmd)
            db.commit()
        except Exception:
            db.rollback()
        cur.close()
        self.work_queue.put(db)

    def select(self, sql_cmd: str):
        """
        查询操作
        :param sql_cmd:sql语句
        :return:
        """
        if self._shutdown:
            raise RuntimeError('连接池已经关闭，无法创建新的连接')
        db = self.work_queue.get()
        cur = db.cursor()

        try:

            cur.execute(sql_cmd)

        except pymysql.err.ProgrammingError as e:
            print(e)
            cur.close()
            raise e
        except pymysql.err.IntegrityError as e:
            print(e)
            cur.close()
            raise e
        iterator_pid = cur.fetchall()
        cur.close()
        self.work_queue.put(db)

        return iterator_pid

    def shutdown(self):
        self._shutdown = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.work_queue.empty()