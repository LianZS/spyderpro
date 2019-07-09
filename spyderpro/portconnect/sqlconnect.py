class MysqlOperation():
    def __init__(self):
        pass

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
    def get_cursor(db, sql):

        cursor = db.cursor()
        try:
            cursor.execute(sql)
            db.commit()
            cursor.close()

        except Exception as e:
            print("查询错误%s" % e)
            db.rollback()
            return None
        return cursor