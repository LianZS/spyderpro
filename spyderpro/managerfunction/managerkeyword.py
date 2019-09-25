import datetime
import csv
from spyderpro.port_connect.sql_connect import MysqlOperation
from setting import *
from spyderpro.pool.mysql_connect import ConnectPool
from spyderpro.function.keywordfunction.mobilekey import MobileKey
from spyderpro.function.keywordfunction.searchkeyword import SearchKeyword

rootpath = os.path.dirname(os.path.abspath(os.path.pardir))


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
        关键词网络我搜索频率----这里没要使用并发，因为一天才进行一次
        :return:
        """
        pool = ConnectPool(max_workers=5)
        sql = "select pid,area,flag from digitalsmart.scencemanager "
        data = pool.select(sql)

        search = SearchKeyword()
        today = datetime.datetime.today()
        t = datetime.timedelta(days=2)
        yesterday = int(str((today - t).date()).replace("-", ""))  # 昨天
        pre_yesterday = int(str((today - t - t).date()).replace("-", ""))  # 前天
        for item in data:
            pid: int = item[0]
            area: str = item[1]
            flag: int = item[2]
            searcharea = search.key_check(area)  # 关键词纠正
            baidu = search.baidu_browser_keyword_frequency(searcharea)  # 百度搜索

            if not baidu:
                continue
            last_date = self._get_last_date(pid, area, "baidu")  # 最近更新时间,0表示数据库里没有任何数据
            for sql_cmd in self._sql_format(last_date, baidu, pid, area, flag):
                pool.sumbit(sql_cmd)

            last_date = self._get_last_date(pid, area, "wechat")
            wechat = search.wechat_browser_keyword_frequency(searcharea, startdate=pre_yesterday,
                                                             enddate=yesterday)  # 只获取前2天的数据
            self.sumbit_commit(pid, area, last_date, wechat, flag)
            last_date = self._get_last_date(pid, area, "sougou")

            sougou = search.sougou_browser_keyword_frequency(searcharea, startdate=pre_yesterday,
                                                             enddate=yesterday)  # 获取前两天的数据
            self.sumbit_commit(pid, area, last_date, sougou, flag)
        pool.close()

    def _get_last_date(self, region_id, place, company) -> int:
        """
        获取数据库关键词搜索频率最近的更新时间
        :param region_id:景区id
        :param place:搜索词
        :param company:平台
        :return:
        """
        sql = "select tmp_date from digitalsmart.searchrate where pid={0} and area='{1}' and name='{2}' order by tmp_date".format(
            region_id, place, company)
        pool = ConnectPool(max_workers=1)
        last_date = pool.select(sql)
        if len(last_date) == 0:
            last_date = 0
            print(last_date)
        else:
            last_date = last_date[0][0]
        pool.close()
        return last_date

    def _sql_format(self, last_date, obj, region_id, place, flag):
        """
        格式化sql语句
        :param last_date:最近更新时间
        :param obj:数据对象
        :param region_id:景区id
        :param place:景区
        :param flag:flag类型
        :return:
        """

        if last_date == obj.update:
            return None

        # 更新时间
        update = str(obj.update)
        year = int(update[:4])
        month = int(update[4:6])
        day = int(update[6:])
        # 品牌名
        name = obj.company
        # 格式化时间
        tdate = datetime.datetime(year, month, day)
        # 获取关键词频率
        baiduvalues = list(obj.all_value)
        # 时间间隔
        t = datetime.timedelta(days=len(baiduvalues))
        # 最早点时间
        tdate = tdate - t
        t = datetime.timedelta(days=1)
        for value in baiduvalues:
            tdate += t
            tmp_date = int(str(tdate.date()).replace("-", ""))
            if tmp_date <= last_date:  # 过滤存在的数据
                continue

            rate = value
            sql = "insert into digitalsmart.searchrate(pid, tmp_date, area, rate, name, flag) values " \
                  "(%d,%d,'%s',%d,'%s',%d)" % (region_id, tmp_date, place, rate, name, flag)
            yield sql

    @staticmethod
    def sumbit_commit(pid, area, lastdate, objs, flag):
        pool = ConnectPool(max_workers=1)
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
            pool.sumbit(sql)
        pool.close()
