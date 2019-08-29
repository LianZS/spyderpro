import csv
import os
import pymysql
from threading import Thread, Semaphore

user = 'root'
password = 'lzs87724158'
host = "localhost"
port = 3306
scencefilepath = os.getcwd()
city_file_path = os.getcwd()
database = 'digitalsmart'
db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)

cur = db.cursor()
sql = "select pid,area ,table_id from digitalsmart.tablemanager "
cur.execute(sql)
area_map = dict()
for pid, area, table_id in cur.fetchall():
    area_map[area] = {"pid": pid, "table_id": table_id}

rootpath = os.path.abspath(os.path.curdir)
dirpath = "/Volumes/Tigo/易班项目数据/景区客流数据/"
sql_file = open("./flowdata.sql", 'a+')
for file in os.listdir(dirpath):
    area = file.split(".")[0]
    print(file)
    try:
        id_data = area_map[area]
    except KeyError:
        continue
    pid = id_data['pid']
    table_id = id_data['table_id']
    filepath = dirpath + file
    f = open(filepath, 'r')
    r = csv.reader(f)
    if table_id == 0:
        sql_format = "insert into digitalsmart.historyscenceflow0(pid, ddate, ttime, num) VALUES "
    elif table_id == 1:
        sql_format = "insert into digitalsmart.historyscenceflow1(pid, ddate, ttime, num) VALUES "
    elif table_id == 2:
        sql_format = "insert into digitalsmart.historyscenceflow2 (pid, ddate, ttime, num) VALUES "
    elif table_id == 3:
        sql_format = "insert into digitalsmart.historyscenceflow3 (pid, ddate, ttime, num) VALUES "
    elif table_id == 4:
        sql_format = "insert into digitalsmart.historyscenceflow4 (pid, ddate, ttime, num) VALUES "
    elif table_id == 5:
        sql_format = "insert into digitalsmart.historyscenceflow5 (pid, ddate, ttime, num) VALUES "
    elif table_id == 6:
        sql_format = "insert into digitalsmart.historyscenceflow6 (pid, ddate, ttime, num) VALUES "
    elif table_id == 7:
        sql_format = "insert into digitalsmart.historyscenceflow7 (pid, ddate, ttime, num) VALUES "
    elif table_id == 8:
        sql_format = "insert into digitalsmart.historyscenceflow8 (pid, ddate, ttime, num) VALUES "
    elif table_id == 9:
        sql_format = "insert into digitalsmart.historyscenceflow9 (pid, ddate, ttime, num) VALUES "
    sql_file.write(sql_format)
    item = r.__next__()
    date_time = item[0]  # 2018-04-08 19:05:00
    ddate = int(date_time.split(" ")[0].replace("-", ''))
    ttime = date_time.split(" ")[1]
    num = int(item[1])
    value = "(%d,%d,'%s',%d)" % (pid, ddate, ttime, num)
    sql_file.write(value)
    for item in r:
        try:
            date_time = item[0]  # 2018-04-08 19:05:00
            ddate = int(date_time.split(" ")[0].replace("-", ''))
            ttime = date_time.split(" ")[1]
            num = int(item[1])
        except Exception:
            print(item)
            continue
        value = "(%d,%d,'%s',%d)" % (pid, ddate, ttime, num)
        sql_file.write(",")
        sql_file.write(value)
        break
    sql_file.write(";")
