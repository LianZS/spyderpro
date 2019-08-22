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
sql = "select pid,area,table_id from digitalsmart.tablemanager"
cur.execute(sql)
result = cur.fetchall()
db.close()
path = "/Volumes/Tigo/易班项目数据/FILE/"
lock = Semaphore(10)
for item in result:

    scence_pid = item[0]
    area = item[1]
    scence_table_id = item[2]
    scence_filepath = path + area + ".csv"


    def fast(pid, table_id, filepath):
        try:
            f = open(filepath, 'r')
        except Exception as e:
            lock.release()
            return
        print(filepath)
        read = csv.reader(f)
        count = 0
        db = pymysql.connect(host=host, user=user, password=password, database=database,
                             port=port)

        cur = db.cursor()
        for row in read:
            dd = row[0]
            ddate, ttime = dd.split(" ", maxsplit=2)
            ddate = int(ddate.replace("-", ""))
            num = int(row[1])
            sql = "insert into digitalsmart.historyscenceflow{0} (pid, ddate, ttime, num) VALUE (%d,%d,'%s',%d)".format(
                table_id) % (
                      pid, ddate, ttime, num)

            cur.execute(sql)
            count += 1
            if count % 1001 == 0:
                print("commit")
                db.commit()
        db.commit()
        db.close()
        lock.release()


    lock.acquire()
    Thread(target=fast, args=(scence_pid, scence_table_id, scence_filepath,)).start()
