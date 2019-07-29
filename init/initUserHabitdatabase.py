import csv
import sys
import os

sys.path[0] = os.path.abspath(os.path.curdir)
from setting import *

rootpath = os.path.abspath(os.path.pardir)

db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)
cur = db.cursor()


def initUserHabit():
    sql = "select id from digitalsmart.userhabit"
    cur.execute(sql)
    if len(cur.fetchall()) >= 10:
        print("整体用户应用安装行为userhabit数据库已经初始化了")
        return
    filepath = os.path.join(rootpath, 'datafile/normalInfo/整体用户行为.csv')
    f = open(filepath)
    r = csv.reader(f)
    r.__next__()
    for item in r:  # 日期,人均安装应用,人均启动应用
        ddate = item[0]
        aver_install = int(item[1])
        aver_start = int(item[2])
        sql = "insert into digitalsmart.userhabit(ddate, installnum, activenum) value ('%s',%d,%d)" % (
            ddate, aver_install, aver_start)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
    f.close()


if __name__ == "__main__":
    initUserHabit()
    cur.close()
    db.close()
