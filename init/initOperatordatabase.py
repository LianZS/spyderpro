import csv
import sys
import os

sys.path[0] = os.path.abspath(os.path.curdir)
from setting import *

rootpath = os.path.abspath(os.path.pardir)

db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)
cur = db.cursor()


def initOperator():
    """
    初始化运营商operator数据库

    """
    sql = 'select id from digitalsmart.operator'
    cur.execute(sql)
    if len(cur.fetchall()) >= 4:
        print("运营商operator已经初始化了")
        return
    pids = [1, 2, 3, 4]
    operators = ["中国移动", "中国联通", "中国电信", "其他"]
    for pid, operator in zip(pids, operators):
        sql = "insert into digitalsmart.operator(id, name) VALUE (%d,'%s')" % (pid, operator)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()


def initOperatorRate():
    """初始化运营商发展情况operatorrate 数据库"""
    sql = 'select id from digitalsmart.operatorrate'
    cur.execute(sql)
    if len(cur.fetchall()) >= 10:
        print("运营商发展情况operatorrate已经初始化了")
        return

    sql = "select id,name from digitalsmart.operator"
    cur.execute(sql)
    operatorMap = dict()
    for item in cur.fetchall():
        operatorMap[item[1]] = item[0]

    filepath = os.path.join(rootpath, 'datafile/normalInfo/运营商占有率.csv')
    f = open(filepath)
    r = csv.reader(f)
    r.__next__()
    for item in r:  # (运营商,日期,占有率)
        operator = item[0]
        pid = operatorMap[operator]
        ddate = item[1]
        rate = float(item[2])
        sql = "insert into digitalsmart.operatorrate(pid, ddate, rate) VALUE (%d,'%s',%f)" \
              % (pid, ddate, rate)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
    f.close()


def initNetWork():
    """初始化网络概况表"""

    sql = "select id from  digitalsmart.network"
    cur.execute(sql)
    if len(cur.fetchall()) >= 4:
        print("网络概况network数据库已经初始化了")
        return
    pids = [1, 2, 3, 4, 5, 6]
    networks = ["2G", "3G", "4G", "WIFI", "5G", "其他"]
    for pid, network in zip(pids, networks):
        sql = "insert into digitalsmart.network(id, name) VALUE (%d,'%s')" % (pid, network)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()


def initNetWorkShare():
    sql = "select id from digitalsmart.networkshare"
    cur.execute(sql)
    if len(cur.fetchall()) >= 40:
        print("网络发展情况networkshare数据库已经初始化了")
        return
    sql = "select id,name from digitalsmart.network"
    cur.execute(sql)
    result = cur.fetchall()
    if not result:
        return
    networkMap = dict()
    for item in result:
        networkMap[item[1]] = item[0]
    filepath = os.path.join(rootpath, 'datafile/normalInfo/网络占有率.csv')
    f = open(filepath)
    r = csv.reader(f)
    r.__next__()
    print(networkMap)
    for item in r:  # (网络,日期,占有率)
        network = item[0]
        pid = networkMap[network]
        ddate = item[1]
        rate = float(item[2])
        sql = "insert into digitalsmart.networkshare(pid, ddate, rate) VALUE (%d,'%s',%f)" % (pid, ddate, rate)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
    f.close()


if __name__ == "__main__":
    initOperator()
    initOperatorRate()
    initNetWork()
    initNetWorkShare()
    cur.close()
    db.close()
