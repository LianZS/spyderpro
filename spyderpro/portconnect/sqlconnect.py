from pymysql.cursors import Cursor


class MysqlOperation():
    def __init__(self):
        pass

    def write_data(self, db, sql) -> bool:
        """
        数据库写入
        :param db:数据库实例
        :param sql:sql执行语句
        :return:
        """

        if not self.loaddatabase(db, sql):
            print("插入出错")
            return False

        return True

    @staticmethod
    def loaddatabase(db, sql) -> bool:
        """
        数据库写入操作
        :param db:
        :param sql:
        :return:
        """

        cursor = db.cursor()
        try:
            cursor.execute(sql)
            db.commit()
            cursor.close()

        except Exception as e:

            print("error:%s" % e)
            db.rollback()
            return False
        return True

    @staticmethod
    def get_cursor(db, sql) -> Cursor:

        cursor = db.cursor()
        try:
            cursor.execute(sql)
            db.commit()
            cursor.close()

        except Exception as e:
            print("查询错误%s" % e)
            print(sql)
            db.rollback()
            return "error"
        return cursor
