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
sql_file = open("./newweatherdb.sql", 'a+')
sql_file.write("insert into digitalsmart.weatherdb(pid, ddate, weatherstate, template, wind) VALUES ")
for filename in os.listdir("/Users/darkmoon/Project/SpyderPr/spyderpro/models/weather/Weather"):
    filepath = "/Users/darkmoon/Project/SpyderPr/spyderpro/models/weather/Weather/" + filename
    f = open(filepath, 'r', encoding="UTF-8")
    r = csv.reader(f)
    city = filename.split(".")[0]

    try:
        pid = city_map[city]

    except KeyError:
        continue
    count = 1

    for item in r:
        ddate = item[0]
        state = item[1]
        template = item[2]
        wind = item[3]
        year, month, day = ddate[:4], ddate[5:7], ddate[8:10]
        ddate = int(year + month + day)
        value = "(%d,%d,'%s','%s','%s')" % (pid, ddate, state, template, wind)
        sql_file.write(value)
        # sql = "insert into digitalsmart.weatherdb(pid, ddate, weatherstate, template, wind) VALUE (%d,%d,'%s','%s','%s')" % (
        #     pid, ddate, state, template, wind)
        # print(sql)
        #     cur.execute(sql)
        #     count += 1
        #     if count % 1111 == 0:
        #         db.commit()
        #         count = 1
        # db.commit()
        sql_file.write(",")

sql_file.write(";")
