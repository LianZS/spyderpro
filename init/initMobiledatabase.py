import csv
import sys
import os

sys.path[0] = os.path.abspath(os.path.curdir)
from setting import *

rootpath = os.path.abspath(os.path.pardir)

db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)
cur = db.cursor()


def initMobileBrand():
    """
    初始化品牌概况表
    :return:
    """
    sql = 'select id from digitalsmart.mobilebrand'
    cur.execute(sql)
    if len(cur.fetchall()) >= 100:
        print("品牌概况表mobilebrand已经初始化了")
        return
    filepath = os.path.join(rootpath, 'datafile/normalInfo/品牌.csv')
    f = open(filepath, 'r')
    r = csv.reader(f)
    r.__next__()

    for item in r:  # (id,brand)
        pid = int(item[0])
        brand = item[1]
        sql = "insert into digitalsmart.mobilebrand (id, name) value (%d,'%s')" % (pid, brand)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()

    print("over")


def initBrandShare():
    """
    品牌占有率
    :return:
    """
    sql = 'select id from digitalsmart.brandshare'
    cur.execute(sql)
    if len(cur.fetchall()) >= 100:
        print("品牌占有率brandshare已经初始化了")
        return
    sql = "select name,id from digitalsmart.mobilebrand"
    try:
        cur.execute(sql)
        db.commit()
    except Exception:
        db.rollback()
        return
    result = cur.fetchall()
    if result is None:
        return
    brandMap = dict()
    for item in result:  # 获取品牌标识
        brandMap[item[0]] = item[1]
    filepath = os.path.join(rootpath, 'datafile/normalInfo/品牌占有率.csv')
    f = open(filepath, 'r')
    r = csv.reader(f)
    r.__next__()

    for item in r:
        brand = item[0]
        ddate = item[1]
        rate = float(item[2])
        pid = brandMap[brand]
        sql = "insert into digitalsmart.brandshare (pid, ddate, rate) VALUE (%d,'%s',%f)" % (
            pid, ddate, rate)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e, brand, ddate)
            db.rollback()
    print("over")


def initMobileModel():
    """

    初始化手机占有率:
    """
    sql = 'select id from digitalsmart.mobilemodel'
    cur.execute(sql)
    if len(cur.fetchall()) >= 1000:
        print("品牌手机机型占有率mobilemodel已经初始化了")
        return
    sql = "select name,id from digitalsmart.mobilebrand"
    try:
        cur.execute(sql)
        db.commit()
    except Exception:
        db.rollback()
        return
    result = cur.fetchall()
    if result is None:
        return
    brandMap = dict()
    for item in result:  # 获取品牌标识
        brandMap[item[0]] = item[1]
    mpid = 0

    filepath = os.path.join(rootpath, 'datafile/normalInfo/安卓手机品牌占有率.csv')
    f = open(filepath, 'r')
    r = csv.reader(f)
    r.__next__()
    mtypelist = list()
    data = list(r)
    # 获取机型
    for android in data:  # 品牌,机型,日期,占有率
        mobiletype = android[1]
        mtypelist.append(mobiletype)
    mtypeSet = set(mtypelist)  # 过滤重复
    mobileMap = dict()
    for mtype in mtypeSet:  # 机型键值对
        mpid += 1
        mobileMap[mtype] = mpid
    for android in data:  # (品牌,机型,日期,占有率)
        brand = android[0]
        mtype = android[1]

        ddate = android[2]
        rate = float(android[3])
        pid = brandMap[brand]
        mpid = mobileMap[mtype]
        sql = "insert into digitalsmart.mobilemodel(mpid, mmodel, ddate, rate, pid, brandtype)value " \
              "(%d,'%s','%s',%f,%d,'%s')" % (mpid, mtype, ddate, rate, pid, "安卓")
        cur.execute(sql)
        db.commit()
    f.close()

    filepath = os.path.join(rootpath, 'datafile/normalInfo/苹果手机品牌占有率.csv')
    f = open(filepath, 'r')
    r = csv.reader(f)
    r.__next__()
    mtypelist = list()
    data = list(r)

    for iphone in data:
        mobiletype = iphone[0] + " " + iphone[1]
        mtypelist.append(mobiletype)
    mtypeSet = set(mtypelist)
    mobileMap = dict()
    for mtype in mtypeSet:
        mpid += 1
        mobileMap[mtype] = mpid
    for iphone in data:  # (品牌,机型,日期,占有率)
        brand = "苹果"
        mtype1 = iphone[0]
        mtype2 = iphone[1]
        mtype = mtype1 + " " + mtype2
        ddate = iphone[2]
        rate = float(iphone[3])
        pid = brandMap[brand]
        mpid = mobileMap[mtype]
        sql = "insert into digitalsmart.mobilemodel(mpid, mmodel, ddate, rate, pid, brandtype)value " \
              "(%d,'%s','%s',%f,%d,'%s')" % (mpid, mtype, ddate, rate, pid, "苹果")
        cur.execute(sql)
        db.commit()


def initMobileSystem():
    """初始化手机系统版本情况"""
    sql = 'select id from digitalsmart.mobilesystemversion'
    cur.execute(sql)
    if len(cur.fetchall()) >= 20:
        print("手机系统版本情况mobilesystemversion已经初始化了")
        return
    """录入安卓系统版本"""
    filepath = os.path.join(rootpath, 'datafile/normalInfo/安卓系统占有率.csv')
    f = open(filepath)
    r = csv.reader(f)
    r.__next__()
    versionlist = list()
    for item in r:  # (系统,日期,占有率)
        version = item[0]
        versionlist.append(version)
    versionSet = set(versionlist)
    pid = 0  # 系统标识
    for version in versionSet:
        pid += 1
        sql = "insert into digitalsmart.mobilesystemversion(id, version,category) VALUE (%d,'%s','%s')" % \
              (pid, version, "安卓")
        cur.execute(sql)
    db.commit()
    f.close()
    """录入苹果系统版本"""

    filepath = os.path.join(rootpath, 'datafile/normalInfo/苹果系统占有率.csv')
    f = open(filepath)
    r = csv.reader(f)
    r.__next__()
    versionlist = list()
    for item in r:  # (系统,日期,占有率)
        version = "OS " + item[0]
        versionlist.append(version)
    versionSet = set(versionlist)
    for version in versionSet:
        pid += 1
        sql = "insert into digitalsmart.mobilesystemversion(id, version,category) VALUE (%d,'%s','%s')" % \
              (pid, version, "苹果")
        cur.execute(sql)
    db.commit()


def initMobileSystemRate():
    sql = 'select id from digitalsmart.mobilesystemrate'
    cur.execute(sql)
    if len(cur.fetchall()) >= 100:
        print("手机系统占有率情况mobilesystemrate已经初始化了")
        return

    sql = "select id,version from digitalsmart.mobilesystemversion"
    cur.execute(sql)
    if not cur:
        print("mobilesystemversion还未初始化")
        return
    systemMap = dict()
    for item in cur.fetchall():
        systemMap[item[1]] = item[0]
    # 录入安卓数据
    filepath = os.path.join(rootpath, 'datafile/normalInfo/安卓系统占有率.csv')
    f = open(filepath)
    r = csv.reader(f)
    r.__next__()
    for item in r:  # (系统,日期,占有率)
        version = item[0]
        pid = systemMap[version]
        ddate = item[1]
        rate = float(item[2])
        sql = "insert into digitalsmart.mobilesystemrate(pid, ddate, rate) VALUE (%d,'%s',%f)" % (pid, ddate, rate)

        cur.execute(sql)
    db.commit()
    f.close()
    """录入苹果系统版本"""

    filepath = os.path.join(rootpath, 'datafile/normalInfo/苹果系统占有率.csv')
    f = open(filepath)
    r = csv.reader(f)
    r.__next__()
    for item in r:  # (系统,日期,占有率)
        version = "OS " + item[0]
        pid = systemMap[version]
        ddate = item[1]
        rate = float(item[2])
        sql = "insert into digitalsmart.mobilesystemrate(pid, ddate, rate) VALUE (%d,'%s',%f)" % (pid, ddate, rate)

        cur.execute(sql)
    db.commit()
    f.close()


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
        cur.execute(sql)
    db.commit()


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
        cur.execute(sql)
    db.commit()
    f.close()


if __name__ == "__main__":
    initMobileBrand()
    initBrandShare()
    initMobileModel()
    initMobileSystem()
    initMobileSystemRate()
    initOperator()
    initOperatorRate()
    cur.close()
    db.close()
