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
dirpath = rootpath + "/FILE/"
lock = Semaphore(5)
for file in os.listdir(dirpath):
    area = file.split(".")[0]
    id_data = area_map[area]
    pid = id_data['pid']
    table_id = id_data['table_id']
    filepath = dirpath + file
    f = open(filepath, 'r')
    r = csv.reader(f)


    def fast(file_read, scence_pid, histtory_table_id):
        db = pymysql.connect(host=host, user=user, password=password, database=database,
                             port=port)

        cur = db.cursor()
        sql_format = None
        if histtory_table_id == 0:
            sql_format = "insert into digitalsmart.historyscenceflow0(pid, ddate, ttime, num) VALUE (%d,%d,'%s',%d)"
        elif histtory_table_id == 1:
            sql_format = "insert into digitalsmart.historyscenceflow1(pid, ddate, ttime, num) VALUE (%d,%d,'%s',%d)"
        elif histtory_table_id == 2:
            sql_format = "insert into digitalsmart.historyscenceflow2 (pid, ddate, ttime, num) VALUE (%d,%d,'%s',%d)"
        elif histtory_table_id == 3:
            sql_format = "insert into digitalsmart.historyscenceflow3 (pid, ddate, ttime, num) VALUE (%d,%d,'%s',%d)"
        elif histtory_table_id == 4:
            sql_format = "insert into digitalsmart.historyscenceflow4 (pid, ddate, ttime, num) VALUE (%d,%d,'%s',%d)"
        elif histtory_table_id == 5:
            sql_format = "insert into digitalsmart.historyscenceflow5 (pid, ddate, ttime, num) VALUE (%d,%d,'%s',%d)"
        elif histtory_table_id == 6:
            sql_format = "insert into digitalsmart.historyscenceflow6 (pid, ddate, ttime, num) VALUE (%d,%d,'%s',%d)"
        elif histtory_table_id == 7:
            sql_format = "insert into digitalsmart.historyscenceflow7 (pid, ddate, ttime, num) VALUE (%d,%d,'%s',%d)"
        elif histtory_table_id == 8:
            sql_format = "insert into digitalsmart.historyscenceflow8 (pid, ddate, ttime, num) VALUE (%d,%d,'%s',%d)"
        elif histtory_table_id == 9:
            sql_format = "insert into digitalsmart.historyscenceflow9 (pid, ddate, ttime, num) VALUE (%d,%d,'%s',%d)"
        count = 1
        for item in file_read:
            date_time = item[0]  # 2018-04-08 19:05:00
            ddate = int(date_time.split(" ")[0].replace("-", ''))
            ttime = date_time.split(" ")[1]
            num = int(item[1])
            sql = sql_format % (scence_pid, ddate, ttime, num)
            cur.execute(sql)
            count += 1
            if count % 1111 == 0:
                db.commit()
                count = 0
        db.commit()
        cur.close()
        db.close()
        lock.release()


    lock.acquire()
    print(area,pid,table_id)
    Thread(target=fast, args=(r, pid, table_id,)).start()
