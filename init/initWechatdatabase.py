import csv
import sys
import os

sys.path[0] = os.path.abspath(os.path.curdir)
from setting import *

rootpath = os.path.abspath(os.path.pardir)

db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)
cur = db.cursor()


def initWechatPublic_Info():
    """
    初始化微信公众号列表

    """
    sql = "select id from digitalsmart.wechatpublic"
    cur.execute(sql)
    result = cur.fetchall()
    if len(result) > 100000:
        print("微信公众号概况表wechatpublic已经初始化")
        return None

    filepath = os.path.join(rootpath, 'datafile/normalInfo/wechatinfo.csv')
    f = open(filepath)
    r = csv.reader(f)
    r.__next__()
    for pid, name, idcard in r:  ##(标识,公众号名,公众号id)
        pid = int(pid)
        sql = """insert into digitalsmart.wechatpublic(id, name, idcard) VALUE (%d,'%s','%s')""" % (pid, name, idcard)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()


if __name__ == "__main__":
    initWechatPublic_Info()
    cur.close()
    db.close()
