from .celeryconfig import app
import pymysql

import os
import re

rootpath = os.path.dirname(os.path.abspath(os.path.pardir))


@app.task(queue='clear')
def clear_mysql_log_bin():
    root = "/var/lib/mysql/"
    log_regular = "mysql_log_bin."
    file_map = dict()
    for filename in os.listdir(root):
        if log_regular in filename:
            temp_filename = filename
            # 文件尾部序列号
            file_set = temp_filename.replace(log_regular, '')
            match = re.match("\d+", file_set)
            if match is None:
                continue
            file_map[filename] = file_set
    sort_file_list = sorted(file_map.keys(), key=lambda x: file_map[x])
    for file in sort_file_list[:-1]:
        filepath = root + file
        os.remove(filepath)


@app.task(queue='clear')
def clear_mysql():
    """
    情况人流数据分布表
    :return:
    """
    user = 'root'
    password = 'lzs87724158'
    host = "localhost"
    port = 3306
    database = 'digitalsmart'

    db = pymysql.connect(host=host, user=user, password=password, database=database,
                         port=port)
    cur = db.cursor()
    for i in range(1, 444):
        sql = "truncate table peopleposition{table_id} ;".format(table_id=i)
        cur.execute(sql)
        db.commit()
