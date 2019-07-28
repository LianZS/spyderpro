import csv
import sys
import os

sys.path[0] = os.path.abspath(os.path.curdir)
from setting import *

rootpath = os.path.abspath(os.path.pardir)

db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)
cur = db.cursor()


def inintdatbaseOfscencemanager():
    sql = 'select id from digitalsmart.scencemanager'
    cur.execute(sql)
    if len(cur.fetchall()) >= 500:
        print("信息概况总表scencemanager已经初始化了")
        return
    filepath = os.path.join(rootpath, 'datafile/normalInfo/scenceinfo.csv')
    f = open(filepath, 'r')
    read = csv.reader(f)
    read.__next__()
    # 城市,地名,地区标识,城市标识,天气标识,类别,中心经度,中心维度,经纬度范围

    for item in read:
        province = item[0]
        city = item[1]
        area = item[2]
        pid = int(item[3])
        citypid = int(item[4])
        weatherpid = int(item[5])
        flag = int(item[6])

        lon = float(item[7])
        lat = float(item[8])
        sql = "insert into digitalsmart.scencemanager" \
              "(province,pid, area, longitude, latitude, loaction, citypid, weatherpid,flag) VALUE " \
              "('%s',%d,'%s',%f,%f,'%s',%d,%d,%d)" % (province, pid, area, lon, lat, city, citypid, weatherpid, flag)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
    print("success")


def initTableManager():
    """
    初始化人口分表管理tablemanager
    :return:
    """
    sql = 'select id from digitalsmart.tablemanager'
    cur.execute(sql)
    if len(cur.fetchall()) >= 500:
        print("人口分表管理tablemanager已经初始化了")
        return
    filepath = os.path.join(rootpath, 'datafile/normalInfo/scenceinfo.csv')
    f = open(filepath, 'r')
    read = csv.reader(f)
    read.__next__()
    #  省份,城市,地名,地区标识,城市标识,天气标识,类别,中心经度,中心维度,经纬度范围
    count = 0  # 存一张表中90个景区，一共7张
    table = -1
    for item in read:
        count += 1
        table += 1

        area = item[2]
        pid = int(item[3])
        flag = int(item[6])
        sql = "insert into digitalsmart.tablemanager(area, pid, last_date, table_id,flag) VALUE ('%s',%d,%d,%d,%d)" % (
            area, pid, 0, table, flag)
        # sql = "update digitalsmart.tablemanager set flag={0} where pid={1} and area={2}".format(flag, pid, "'"+area+"'")
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
        if count % 10 == 0:
            count = 0
            table = -1
    # cur.close()


def initCitymanager():
    sql = 'select id from digitalsmart.citymanager'
    cur.execute(sql)
    if len(cur.fetchall()) >= 100:
        print("城市标识表citymanager已经初始化了")
        return
    filepath = os.path.join(rootpath, 'datafile/normalInfo/trafficinfo.csv')
    f = open(filepath, 'r')
    read = csv.reader(f)
    read.__next__()  # 城市名,城市id,维度,经度,年度id

    for item in read:
        city = item[0]
        pid = int(item[1])
        lat = float(item[2])
        lon = float(item[3])
        yearpid = int(item[4])
        if yearpid == 0:
            yearpid = pid
        weatherpid = "--"
        sql = "insert into digitalsmart.citymanager(pid, name, longitude, latitude, weatherpid, yearpid) " \
              "VALUE (%d,'%s',%f,%f,'%s',%d)" % (pid, city, lon, lat, weatherpid, yearpid)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()


def initGeographic():
    sql = 'select id from digitalsmart.geographic'
    cur.execute(sql)
    if len(cur.fetchall()) >= 500:
        print("地区范围经纬度geographic已经初始化了")
        return
    filepath = os.path.join(rootpath, 'datafile/normalInfo/scenceinfo.csv')
    f = open(filepath, 'r')
    read = csv.reader(f)
    read.__next__()  # 省份,城市,地名,地区标识,城市标识,天气标识,类别,中心经度,中心维度,经纬度范围
    for item in read:
        pid = int(item[3])
        area = item[2]
        bounds = item[9]
        flag = int(item[6])
        if ";" in bounds:
            bounds = bounds.split(";")
            for latlon in bounds:

                if len(latlon) == 0:
                    continue
                lon, lat = eval(latlon)
                sql = "insert into digitalsmart.geographic(pid, longitude, latitude,flag) VALUE (%d,%f,%f,%d)" % \
                      (pid, lon, lat, flag)
                cur.execute(sql)
            db.commit()
        elif "|" in bounds:
            bounds = bounds.split("|")
            for latlon in bounds:

                if len(latlon) == 0:
                    continue
                lat, lon = eval(latlon)
                sql = "insert into digitalsmart.geographic(pid, longitude, latitude,flag) VALUE (%d,%f,%f,%d)" % \
                      (pid, lon, lat, flag)
                cur.execute(sql)
            db.commit()


def initRoadManager():
    """
     初始化道路管理
    """
    sql = 'select id from digitalsmart.roadmanager'
    cur.execute(sql)
    if len(cur.fetchall()) >= 100:
        print("道路管理roadmanager已经初始化了")
        return
    filepath = os.path.join(rootpath, 'datafile/normalInfo/trafficinfo.csv')
    f = open(filepath, 'r')
    read = csv.reader(f)
    read.__next__()  # 城市名,城市id,维度,经度,年度id

    for item in read:
        city = item[0]
        pid = int(item[1])
        for i in range(10):
            sql = "insert into digitalsmart.roadmanager( pid, roadid, up_date, city) value (%d,%d,%d,'%s')" % (
                pid, i, 0, city)
            cur.execute(sql)
    db.commit()


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
    filepath = os.path.join(rootpath, 'datafile/normalInfo/品牌占有率.csv')
    f = open(filepath, 'r')
    r = csv.reader(f)
    r.__next__()
    readlist = list(r)
    brandlist = list()  # 品牌容器
    for item in readlist:  # (品牌,日期,占有率)
        brandlist.append(item[0])
    brandMap = dict()
    brandSet = set(brandlist)
    pid = 0
    for item in brandSet:
        brandMap[item] = pid  # {品牌：品牌id}
        pid += 1
        sql = "insert into digitalsmart.mobilebrand (id, name) value (%d,'%s')" % (pid, item)
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()

    print("over")


def initBrandShare():
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
    sql = 'select id from digitalsmart.mobilemodel'
    cur.execute(sql)
    if len(cur.fetchall()) >= 1000:
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


if __name__ == "__main__":
    # inintdatbaseOfscencemanager()
    # initTableManager()
    # initCitymanager()
    # initGeographic()
    # initRoadManager()
    # initMobileBrand()
    # initBrandShare()
    initMobileModel()
    cur.close()
    db.close()
