import pymysql
import  os
import  csv
user = 'root'
password = 'lzs87724158'
host = "localhost"
port = 3306
database = 'digitalsmart'
db = pymysql.connect(host=host, user=user, password=password, database=database,
                     port=port)

cur = db.cursor()
i = 1
for filename in os.listdir("/Volumes/Tigo/易班项目数据/Weather"):
    city = filename.split(".")[0]
    sql = "insert into digitalsmart.weathermanager(id, city) value (%d,'%s')"%(i,city)
    cur.execute(sql)
    i+=1
db.commit()
