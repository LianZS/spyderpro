from .celeryconfig import app

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
