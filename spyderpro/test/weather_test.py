import pymysql
import os
import csv

user = 'root'
password = 'lzs87724158'
host = "localhost"
port = 3306
database = 'digitalsmart'
db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)

cur = db.cursor()
i = 1

sql = "select id,city from  digitalsmart.weathermanager"
cur.execute(sql)
city_map = dict()
for pid, city in cur.fetchall():
    city_map[city] = pid
for filename in os.listdir("/Volumes/Tigo/易班项目数据/Weather"):
    filepath = "/Volumes/Tigo/易班项目数据/Weather/" + filename
    f = open(filepath, 'r', encoding="gbk")
    r = csv.reader(f)
    city = filename.split(".")[0]
    print(city)
    pid = city_map[city]
    count = 1
    for item in r:
        ddate = item[0]
        state = item[1]
        template = item[2]
        wind = item[3]
        year, month, day = ddate[:4], ddate[5:7], ddate[8:10]
        ddate = int(year + month + day)
        sql = "insert into digitalsmart.weatherdb(pid, ddate, weatherstate, template, wind) VALUE (%d,%d,'%s','%s','%s')" % (
            pid, ddate, state, template, wind)
        cur.execute(sql)
        count += 1
        if count % 1111 == 0:
            db.commit()
            count = 1
    db.commit()
