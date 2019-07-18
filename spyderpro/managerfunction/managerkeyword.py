import datetime
from spyderpro.managerfunction.setting import *
from spyderpro.function.keywordfunction.mobilekey import MobileKey
from spyderpro.function.keywordfunction.searchkeyword import SearchKeyword
from spyderpro.function.keywordfunction.apphabit import AppUserhabit


class ManagerMobileKey(MobileKey):
    def manager_mobile_type_rate(self, year: int, startmonth: int = None, endmonth: int = None):
        data = self.request_mobile_type_rate(year=year, startmonth=startmonth, endmonth=endmonth)
        db = pymysql.connect(host=host, user=user, password=password, database=internetdata,
                             port=port)
        db.connect()
        flag = self.write_mobile_type_rate(db=db, data=data)
        if flag:
            print("success")

    def manager_mobile_brand_rate(self, year: int, startmonth: int = None, endmonth: int = None):
        """

        :param year:
        :param startmonth: 开始月份
        :param endmonth: #结束月份
        """
        data = self.request_mobile_brand_rate(year=year, startmonth=startmonth, endmonth=endmonth)
        db = pymysql.connect(host=host, user=user, password=password, database=internetdata,
                             port=port)
        db.connect()
        flag = self.write_mobile_brand_rate(db=db, data=data)
        if flag:
            print("success")

    def manager_mobile_system_rate(self, year: int, startmonth: int = None, endmonth: int = None):
        data = self.request_mobile_system_rate(year=year, startmonth=startmonth, endmonth=endmonth)
        db = pymysql.connect(host=host, user=user, password=password, database=internetdata,
                             port=port)
        db.connect()
        flag = self.write_mobile_system_rate(db=db, data=data)
        if flag:
            print("success")

    def manager_mobile_operator_rate(self, year: int, startmonth: int = None, endmonth: int = None):
        data = self.request_mobile_operator_rate(year=year, startmonth=startmonth, endmonth=endmonth)
        db = pymysql.connect(host=host, user=user, password=password, database=internetdata,
                             port=port)
        db.connect()
        flag = self.write_mobile_operator_rate(db=db, data=data)
        if flag:
            print("success")

    def manager_mobile_network_rate(self, year: int, startmonth: int = None, endmonth: int = None):
        data = self.request_mobile_network_rate(year=year, startmonth=startmonth, endmonth=endmonth)
        db = pymysql.connect(host=host, user=user, password=password, database=internetdata,
                             port=port)
        db.connect()
        flag = self.write_mobile_network_rate(db=db, data=data)
        if flag:
            print("success")

    def manager_search(self):
        """
        关键词网络我搜索频率
        :return:
        """
        db = pymysql.connect(host=host, user=user, password=password, database='digitalsmart',
                             port=port)
        search = SearchKeyword()
        pid = 11
        area = '白云山'

        baidu, wetchat, sougou = search.browser_keyword_frequency(area)

        def sql_format(obj, pid, area):
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
                rate = value
                sql = "insert into digitalsmart.searchrate(pid, tmp_date, area, rate, name) values " \
                      "('%d','%d','%s','%d','%s')" % (pid, tmp_date, area, rate, name)
                yield sql

        for sql in sql_format(baidu, pid, area):
            self.write_data(db, sql)
        for sql in sql_format(wetchat, pid, area):
            self.write_data(db, sql)
        for sql in sql_format(sougou, pid, area):
            self.write_data(db, sql)

    def manager_app_portrait(self):
        app = AppUserhabit()
        app.get_user_portrait(1, 1, 2)

    def manager_user_behavior(self):
        app = AppUserhabit()
        app.get_user_behavior(1, 1)

    def manager_app_userhabit(self):
        app = AppUserhabit()
        app.get_app_userhabit('qq', '2012-01-01')  # 这个功能还未修改成功


ManagerMobileKey().manager_search()
