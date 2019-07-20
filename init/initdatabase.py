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
    filepath = os.path.join(rootpath, 'datafile/scenceinfo.csv')
    f = open(filepath, 'r')
    read = csv.reader(f)
    read.__next__()
    # 城市,地名,标识,中心经度,中心维度,经纬度范围,类别

    for item in read:
        city = item[0]
        area = item[1]
        pid = int(item[2])
        lon = float(item[3])
        lat = float(item[4])
        weatherpid = 0
        citypid = 0
        flag = int(item[6])
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
    filepath = os.path.join(rootpath, 'datafile/scenceinfo.csv')
    f = open(filepath, 'r')
    read = csv.reader(f)
    read.__next__()
    # 城市,地名,标识,中心经度,中心维度,经纬度范围,类别
    count = 0  # 存一张表中90个景区，一共7张
    table = 0
    for item in read:
        if count % 90 == 0:
            count = 0
            table += 1
        area = item[1]
        pid = int(item[2])
        sql = "insert into digitalsmart.tablemanager(area, pid, last_date, table_id) VALUE ('%s',%d,%d,%d)" % (
            area, pid, 0, table)
        count += 1
        try:
            cur.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
    # cur.close()


if __name__ == "__main__":
    inintdatbaseOfscencemanager()
    initTableManager()
    cur.close()
    db.close()
