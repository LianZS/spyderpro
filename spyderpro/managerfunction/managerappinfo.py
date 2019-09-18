import datetime
import csv
from threading import Thread, Semaphore

from queue import Queue
from spyderpro.tool.mysql_connect import ConnectPool
from spyderpro.portconnect.sqlconnect import MysqlOperation
from setting import *
from spyderpro.function.keywordfunction.mobilekey import MobileKey
from spyderpro.function.keywordfunction.apphabit import AppUserhabit

rootpath = os.path.dirname(os.path.abspath(os.path.pardir))


class ManagerApp(MobileKey, MysqlOperation):

    def manager_app_portrait(self):
        app = AppUserhabit()
        app.get_user_portrait(1, 1, 2)

    def manager_user_behavior(self, filepath: str):
        """
        获取用户行为
        :return:
        """
        f = open(filepath, 'a+', newline='')
        w = csv.writer(f)

        app = AppUserhabit()
        w.writerow(["日期", "人均安装应用", "人均启动应用"])
        year = 2017
        month = 2

        while 1:
            starttime = datetime.datetime(year, month, 1)
            month += 6
            if month > 12:
                year += 1
                month -= 12
            if starttime.year == 2018 and starttime.month > 3:
                break
            result = app.get_user_behavior(starttime.year, starttime.month)
            for item in result:
                date = item.date
                install = item.install
                active_num = item.active_num
                w.writerow([date, install, active_num])
        f.close()

    def manager_app_userhabit(self, appinfo_filepath, appbaseinfo_path):
        """
        获取app用户画像
        :param appinfo_filepath:app信息文件路径
        :param appbaseinfo_path：app基础信息文件写入路径
        :return:
        """
        app = AppUserhabit()
        f = open(appinfo_filepath, 'r')
        read = csv.reader(f)
        # inv = datetime.timedelta(days=31)
        wait = Semaphore(10)
        dataqueue = Queue(20)
        appinfo = csv.writer(open(appbaseinfo_path, 'a+', newline=''))
        appinfo.writerow(['app', '日期', '省份热度', '年龄分布', '性别分布', '内容关键词热度'])

        def fast_request(name, apppid, ddate):  # 请求数据
            response = app.get_app_userhabit(name, apppid, ddate)
            dataqueue.put(response)
            wait.release()

        def deal_data():  # 获取数据

            while 1:
                userhabit = dataqueue.get()
                appinfo.writerow(
                    [userhabit.app, userhabit.ddate, userhabit.province, userhabit.age, userhabit.gender,
                     userhabit.preference])

        Thread(target=deal_data, args=()).start()
        count = 0
        for item in read:
            year = 2017
            month = 1
            day = 1
            count += 1
            # if count < 2294:
            #     continue

            pid = item[0]
            appname = item[1]
            while 1:
                date = datetime.datetime(year, month, day)
                if date.year == 2018 and date.month == 12:
                    break
                wait.acquire()
                Thread(target=fast_request, args=(appname, pid, str(date.date()))).start()
                if month < 12:
                    month += 1
                else:
                    year += 1
                    month = 1

    def manager_app_active_data(self):  # 每个月一次
        """    获取app的用户画像数据,性别占比,年龄分布,省份覆盖率,app用户关键词"""
        pool = ConnectPool(max_workers=10)
        app = AppUserhabit()
        sql = "select id,name from digitalsmart.appinfo"

        result = pool.select(sql)
        if not result:
            return None
        today = datetime.datetime.today()
        # 每次启动都挖掘前2个月的数据
        start_date = str(datetime.datetime(today.year, today.month - 2, 1).date())  # "yyyy-mm-01
        for pid, appname in result:
            obj = app.get_app_active_data(appname, pid, start_date)
            if obj is None:
                continue
            name = obj.app_name  # app名
            date = obj.date  # 时间
            active_num = obj.active_num  # 活跃用户数
            active_rate = obj.active_rate  # 活跃用户率
            rate_hight = obj.rate_hight  # 行业基准
            rate_low = obj.rate_low  # 行业均值
            sql_cmd = "insert into digitalsmart.appactive(pid, ddate, activenum, activerate, base_activerate, aver_activerate) " \
                      "VALUE (%d,'%s',%d,%f,%f,%f)" % (pid, date, active_num, active_rate, rate_hight, rate_low)
            pool.sumbit(sql_cmd)
