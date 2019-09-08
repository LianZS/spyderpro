import abc


class ConnectInterface(abc.ABCMeta):


    @abc.abstractmethod
    def _init_pool_(self):
        """
        初始化连接池
        :return:
        """
        pass
    @abc.abstractmethod
    def sumbit(self, sql_cmd: str):
        """
        插入, 删除，更新操作
        :param sql_cmd:sql语句
        :return:
        """
        pass

    @abc.abstractmethod
    def select(self, sql_cmd: str):
        """
        查询操作
        :param sql_cmd:sql语句
        :return:
        """
        pass

    @abc.abstractmethod
    def shutdown(self):
        """
        关闭连接池
        :return:
        """
        pass
    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
