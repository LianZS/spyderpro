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
            cursor.close()
            return False
        return True
