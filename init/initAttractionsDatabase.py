import csv
import sys
import os

sys.path[0] = os.path.abspath(os.path.curdir)
from setting import *

rootpath = os.path.abspath(os.path.pardir)

db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)
cur = db.cursor()


def inintdatbaseOfscencemanager():  # 如果景点重复，flag=1时，type_flag一定是1，这个需要人工对比的，因为相同景点名字可能不同
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
              "(province,pid, area, longitude, latitude, loaction, citypid, weatherpid,flag,type_flag) VALUE " \
              "('%s',%d,'%s',%f,%f,'%s',%d,%d,%d,%d)" % (
                  province, pid, area, lon, lat, city, citypid, weatherpid, flag, flag)
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


if __name__ == "__main__":
    inintdatbaseOfscencemanager()
    initTableManager()
    initCitymanager()
    initGeographic()
    initRoadManager()

    cur.close()
    db.close()
