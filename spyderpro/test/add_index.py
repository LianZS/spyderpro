"""
添加索引
"""
import pymysql

user = 'root'
password = 'lzs87724158'
host = "localhost"
port = 3306
database = 'digitalsmart'
db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)
cur = db.cursor()
max_sql = "select max(table_id) from digitalsmart.tablemanager "
cur.execute(max_sql)
count = cur.fetchall()[0][0]
for i in range(1, count + 1):
    sql = "create index date_time_num on historyscenceflow{0} (ddate, ttime, num);".format(i)
    cur.execute(sql)
    print(sql)
db.commit()
max_sql = "select max(table_id) from digitalsmart.tablemanager  where flag=0"
cur.execute(max_sql)
count = cur.fetchall()[0][0]
for i in range(1, count + 1):
    sql = "create index tmp_date_index on peopleposition{0} (tmp_date);".format(i)
    cur.execute(sql)
    print(sql)
db.commit()
