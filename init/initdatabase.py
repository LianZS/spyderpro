import csv
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
        city = item[0]
        area = item[1]
        pid = int(item[2])
        citypid = int(item[3])
        weatherpid = int(item[4])
        flag = int(item[5])

        lon = float(item[6])
        lat = float(item[7])
        sql = "insert into digitalsmart.scencemanager" \
              "(pid, area, longitude, latitude, loaction, citypid, weatherpid,flag) VALUE " \
              "(%d,'%s',%f,%f,'%s',%d,%d,%d)" % (pid, area, lon, lat, city, citypid, weatherpid, flag)
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
    #  城市,地名,地区标识,城市标识,天气标识,类别,中心经度,中心维度,经纬度范围
    count = 0  # 存一张表中90个景区，一共7张
    table = -1
    for item in read:
        count += 1
        table += 1

        area = item[1]
        pid = int(item[2])
        sql = "insert into digitalsmart.tablemanager(area, pid, last_date, table_id) VALUE ('%s',%d,%d,%d)" % (
            area, pid, 0, table)

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
    read.__next__()  # 城市,地名,地区标识,城市标识,天气标识,类别,中心经度,中心维度,经纬度范围
    for item in read:
        pid = int(item[2])
        area = item[1]

        bounds = item[8]
        if ";" in bounds:
            bounds = bounds.split(";")
            for latlon in bounds:

                if len(latlon) == 0:
                    continue
                lon, lat = eval(latlon)
                sql = "insert into digitalsmart.geographic(pid, longitude, latitude) VALUE (%d,%f,%f)" % (pid, lon, lat)
                cur.execute(sql)
            db.commit()
        elif "|" in bounds:
            bounds = bounds.split("|")
            for latlon in bounds:

                if len(latlon) == 0:
                    continue
                lat, lon = eval(latlon)
                sql = "insert into digitalsmart.geographic(pid, longitude, latitude) VALUE (%d,%f,%f)" % (pid, lon, lat)
                cur.execute(sql)
            db.commit()


if __name__ == "__main__":
    inintdatbaseOfscencemanager()
    initTableManager()
    initCitymanager()
    initGeographic()
    cur.close()
    db.close()
