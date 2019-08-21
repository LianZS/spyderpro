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
    def manager_mobile_type_rate(self, mobiletype: int, filepath: str):
        """
         获取某个时段的中国境内各手机机型的占有率

        2014/1 ---2018/9
        :param mobiletype:2表示安卓手机，1表示苹果

        """
        f = open(filepath, 'w', newline='')
        w = csv.writer(f)
        w.writerow(['品牌', '机型', '日期', '占有率'])
        for year in range(2014, 2019):

            startmonth = 1
            endmonth = 12
            if year == 2018:
                endmonth = 9
            data = self.request_mobile_type_rate(year=year, startmonth=startmonth, endmonth=endmonth,
                                                 platform=mobiletype)
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

    def manager_mobile_brand_rate(self, filepath: str):
        """
        获取某时段中国境内各手机品牌占用率
        2014/1 ---2018/9

        """
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

    def manager_mobile_system_rate(self, mobiletype: int, filepath: str):
        """
        platform=2表示安卓手机，1表示苹果
        获取某时段中国境内各手机系统版本占用率

        :return:
        """
        f = open(filepath, 'w', newline='')
        w = csv.writer(f)
        w.writerow(['系统', '日期', '占有率'])
        for year in range(2014, 2019):

            startmonth = 1
            endmonth = 12
            if year == 2018:
                endmonth = 9
            data = self.request_mobile_system_rate(year=year, startmonth=startmonth, endmonth=endmonth,
                                                   platform=mobiletype)
            for info in data:
                mobile_system = info.type_name
                value = float(info.value)
                date = info.date
                w.writerow([mobile_system, date, value])
            f.flush()
        f.close()
        # pid = MobileKey.system_dic[mobile_system]

    def manager_mobile_operator_rate(self, filepath: str):
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

    def manager_mobile_network_rate(self, filepath):

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
        sql = "select pid,area,flag from digitalsmart.scencemanager "
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
        yesterday = int(str((today - t).date()).replace("-", ""))#昨天
        yyesterday = int(str((today - t - t).date()).replace("-", ""))#前天
        # today = int(str(today.date()).replace("-", ""))
        for item in data:
            pid: int = item[0]
            area: str = item[1]
            flag: int = item[2]
            searcharea = search.key_check(area)#关键词纠正
            baidu = search.baidu_browser_keyword_frequency(searcharea)#百度搜索

            if not baidu:
                continue
            lastdate = self.last_date(pid, area, "baidu")  # 最近更新时间,0表示数据库里没有任何数据
            for sql in self.sql_format(lastdate, baidu, pid, area, flag):
                try:
                    cur.execute(sql)
                except Exception as e:
                    print(area,e)
                    db.rollback()

            db.commit()

            lastdate = self.last_date(pid, area, "wechat")
            wechat = search.wechat_browser_keyword_frequency(searcharea, startdate=yyesterday,
                                                             enddate=yesterday)  # 只获取前2天的数据
            self.sumbit_commit(pid,area, lastdate,wechat,flag)
            lastdate = self.last_date(pid, area, "sougou")

            sougou = search.sougou_browser_keyword_frequency(searcharea, startdate=yyesterday,
                                                             enddate=yesterday)  # 获取前两天的数据
            self.sumbit_commit(pid,area, lastdate,sougou,flag)

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
            return 0
        return lastdate

    def sql_format(self, lastdate, obj, region_id, place, flag):

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
            sql = "insert into digitalsmart.searchrate(pid, tmp_date, area, rate, name, flag) values " \
                  "(%d,%d,'%s',%d,'%s',%d)" % (region_id, tmp_date, place, rate, name, flag)
            yield sql

    @staticmethod
    def sumbit_commit(pid, area, lastdate, objs, flag):
        # 搜索频率录入数据库
        for item in objs:
            tmp_date = item.update
            if lastdate >= tmp_date:
                continue
            tmp_date = item.update
            rate = item.all_value
            name = item.company
            sql = "insert into digitalsmart.searchrate(pid, tmp_date, area, rate, name,flag) values " \
                  "(%d,%d,'%s',%d,'%s',%d)" % (pid, tmp_date, area, rate, name, flag)
            cur.execute(sql)

        db.commit()


