import sys
import os

sys.path[0] = os.getcwd()
import datetime
import csv
from threading import Thread, Semaphore

from queue import Queue
from spyderpro.portconnect.sqlconnect import MysqlOperation
from setting import *
from spyderpro.function.keywordfunction.mobilekey import MobileKey
from spyderpro.function.keywordfunction.searchkeyword import SearchKeyword
from spyderpro.function.keywordfunction.apphabit import AppUserhabit

rootpath = os.path.dirname(os.path.abspath(os.path.pardir))
db = pymysql.connect(host=host, user=user, password=password, database='digitalsmart',
                     port=port)
cur = db.cursor()


class ManagerMobileKey(MobileKey, MysqlOperation):
    def manager_mobile_type_rate(self):
        """
         获取某个时段的中国境内各手机机型的占有率

        2014/1 ---2018/9

        """
        filepath = os.path.join(rootpath, 'datafile/苹果手机品牌占有率.csv')
        f = open(filepath, 'w', newline='')
        w = csv.writer(f)
        w.writerow(['品牌', '机型', '日期', '占有率'])
        for year in range(2014, 2019):

            startmonth = 1
            endmonth = 12
            if year == 2018:
                endmonth = 9
            data = self.request_mobile_type_rate(year=year, startmonth=startmonth, endmonth=endmonth, platform=1)
            for info in data:

                mobile_info = info.type_name
                array = mobile_info.split(" ", 2)
                brand = array[0]
                # pid = MobileKey.brand_dic[brand]
                try:
                    mobile_type = array[1]
                except Exception:
                    continue
                value = float(info.value)
                date = info.date
                w.writerow([brand, mobile_type, date, value])
            f.flush()
        f.close()

    def manager_mobile_brand_rate(self):
        """
        获取某时段中国境内各手机品牌占用率
        2014/1 ---2018/9

        """
        filepath = os.path.join(rootpath, 'datafile/品牌占有率.csv')
        f = open(filepath, 'w', newline='')
        w = csv.writer(f)
        w.writerow(['品牌', '日期', '占有率'])
        for year in range(2014, 2019):

            startmonth = 1
            endmonth = 12
            if year == 2018:
                endmonth = 9
            data = self.request_mobile_brand_rate(year=year, startmonth=startmonth, endmonth=endmonth)
            for info in data:
                mobile_brand = info.type_name
                # pid = MobileKey.brand_dic[mobile_brand]
                value = float(info.value)
                date = info.date
                w.writerow([mobile_brand, date, value])
            f.flush()
        f.close()

    def manager_mobile_system_rate(self):
        """
        platform=2表示安卓手机，1表示苹果
        获取某时段中国境内各手机系统版本占用率

        :return:
        """
        filepath = os.path.join(rootpath, 'datafile/苹果系统占有率.csv')
        f = open(filepath, 'w', newline='')
        w = csv.writer(f)
        w.writerow(['系统', '日期', '占有率'])
        for year in range(2014, 2019):

            startmonth = 1
            endmonth = 12
            if year == 2018:
                endmonth = 9
            data = self.request_mobile_system_rate(year=year, startmonth=startmonth, endmonth=endmonth, platform=1)
            for info in data:
                mobile_system = info.type_name
                value = float(info.value)
                date = info.date
                w.writerow([mobile_system, date, value])
            f.flush()
        f.close()
        # pid = MobileKey.system_dic[mobile_system]

    def manager_mobile_operator_rate(self):
        filepath = os.path.join(rootpath, 'datafile/运营商占有率.csv')
        f = open(filepath, 'w', newline='')
        w = csv.writer(f)
        w.writerow(['运营商', '日期', '占有率'])
        for year in range(2014, 2019):

            startmonth = 1
            endmonth = 12
            if year == 2018:
                endmonth = 9
            data = self.request_mobile_operator_rate(year=year, startmonth=startmonth, endmonth=endmonth)
            for info in data:
                mobile_operator = info.type_name
                value = float(info.value)
                date = info.date
                # pid = MobileKey.operator_dic[mobile_operator]
                w.writerow([mobile_operator, date, value])
            f.flush()
        f.close()

    def manager_mobile_network_rate(self):

        filepath = os.path.join(rootpath, 'datafile/网络占有率.csv')
        f = open(filepath, 'w', newline='')
        w = csv.writer(f)
        w.writerow(['网络', '日期', '占有率'])
        for year in range(2014, 2019):

            startmonth = 1
            endmonth = 12
            if year == 2018:
                endmonth = 9
            data = self.request_mobile_network_rate(year=year, startmonth=startmonth, endmonth=endmonth)

            for info in data:
                mobile_net = info.type_name
                value = float(info.value)
                date = info.date
                # pid = MobileKey.network_dic[mobile_net]
                w.writerow([mobile_net, date, value])
            f.flush()
        f.close()

    def manager_search(self):
        """
        关键词网络我搜索频率----这里没要使用高并发，因为一天才进行一次
        :return:
        """
        sql = "select pid,area from digitalsmart.scencemanager "
        try:

            cur.execute(sql)
            db.commit()
        except Exception as e:
            db.rollback()
            return
        data = cur.fetchall()
        search = SearchKeyword()
        today = datetime.datetime.today()
        t = datetime.timedelta(days=2)
        yesterday = int(str((today - t).date()).replace("-", ""))

        yyesterday = int(str((today - t - t).date()).replace("-", ""))
        # today = int(str(today.date()).replace("-", ""))
        for item in data:
            pid: int = item[0]
            area: str = item[1]
            searcharea = search.key_check(area)
            baidu = search.baidu_browser_keyword_frequency(searcharea)

            if not baidu:
                continue
            lastdate = self.last_date(pid, area, "baidu")

            def sql_format(obj, region_id, place):

                if lastdate == obj.update:
                    return None

                update = str(obj.update)
                year = int(update[:4])
                month = int(update[4:6])
                day = int(update[6:])
                name = obj.company
                tdate = datetime.datetime(year, month, day)
                baiduvalues = list(obj.all_value)
                t = datetime.timedelta(days=len(baiduvalues))
                tdate = tdate - t
                t = datetime.timedelta(days=1)
                for value in baiduvalues:
                    tdate += t
                    tmp_date = int(str(tdate.date()).replace("-", ""))
                    if tmp_date <= lastdate:  # 过滤存在的数据
                        continue
                    rate = value
                    sql = "insert into digitalsmart.searchrate(pid, tmp_date, area, rate, name) values " \
                          "(%d,%d,'%s',%d,'%s')" % (region_id, tmp_date, place, rate, name)
                    yield sql

            for sql in sql_format(baidu, pid, area):
                try:
                    cur.execute(sql)
                except Exception as e:
                    print(e)
                    db.rollback()
            db.commit()
            lastdate = self.last_date(pid, area, "wechat")
            wechat = search.wechat_browser_keyword_frequency(searcharea, startdate=yyesterday,
                                                             enddate=yesterday)  # 只获取前2天的数据
            for item in wechat:

                tmp_date = item.update
                if lastdate >= tmp_date:
                    continue
                rate = item.all_value
                name = item.company
                sql = "insert into digitalsmart.searchrate(pid, tmp_date, area, rate, name) values " \
                      "(%d,%d,'%s',%d,'%s')" % (pid, tmp_date, area, rate, name)
                cur.execute(sql)
            db.commit()
            sougou = search.sougou_browser_keyword_frequency(searcharea, startdate=yyesterday,
                                                             enddate=yesterday)  # 获取前两天的数据
            for item in sougou:
                tmp_date = item.update
                if lastdate >= tmp_date:
                    continue
                tmp_date = item.update
                rate = item.all_value
                name = item.company
                sql = "insert into digitalsmart.searchrate(pid, tmp_date, area, rate, name) values " \
                      "(%d,%d,'%s',%d,'%s')" % (pid, tmp_date, area, rate, name)
                cur.execute(sql)
            db.commit()

    def last_date(self, region_id, place, company) -> int:
        """
        获取数据库关键词搜索频率最近的更新时间
        :param region_id:
        :param place:
        :param company:
        :return:
        """
        sql = "select tmp_date from digitalsmart.searchrate where pid={0} and area='{1}' and name='{2}' order by tmp_date".format(
            region_id, place, company)

        cur.execute(sql)
        try:
            lastdate = cur.fetchall()[-1][0]
        except IndexError as e:
            print(e)
            return 0
        return lastdate

    def manager_app_portrait(self):
        app = AppUserhabit()
        app.get_user_portrait(1, 1, 2)

    def manager_user_behavior(self):
        """
        获取用户行为
        :return:
        """
        filepath = os.path.join(rootpath, 'datafile/整体用户行为.csv')
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

    def manager_app_userhabit(self):
        app = AppUserhabit()
        filepath = os.path.join(rootpath, 'datafile/normalInfo/app.csv')
        f = open(filepath, 'r')
        read = csv.reader(f)
        inv = datetime.timedelta(days=31)
        wait = Semaphore(10)
        dataqueue = Queue(20)
        appinfo = csv.writer(open(os.path.join(rootpath, 'datafile/appinfo.csv'), 'a+', newline=''))
        appinfo.writerow(['app', '日期', '省份热度', '年龄分布', '性别分布', '内容关键词热度'])

        def fast_request(name, apppid, ddate):  # 请求数据
            response = app.get_app_userhabit(name, apppid, ddate)
            dataqueue.put(response)
            wait.release()

        def deal_data():  # 获取数据

            while 1:
                userhabit = dataqueue.get()
                appinfo.writerow(
                    [ userhabit.app, userhabit.ddate,userhabit.province, userhabit.age, userhabit.gender,
                     userhabit.preference])

        Thread(target=deal_data, args=()).start()
        count = 0
        for item in read:
            year = 2017
            month = 1
            day = 1
            print(item)
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


if __name__ == "__main__":
    manager = ManagerMobileKey()
    # manager.manager_search()
    # manager.manager_user_behavior()
    # manager.manager_mobile_type_rate()
    # manager.manager_mobile_brand_rate()
    # manager.manager_mobile_system_rate()
    # manager.manager_mobile_operator_rate()
    # manager.manager_mobile_network_rate()
    manager.manager_app_userhabit()
