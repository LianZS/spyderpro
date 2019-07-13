from .setting import *
from spyderpro.function.keywordfunction.mobilekey import MobileKey
from spyderpro.function.keywordfunction.searchkeyword import SearchKeyword


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
        search = SearchKeyword()
        search.browser_keyword_frequency("python")
