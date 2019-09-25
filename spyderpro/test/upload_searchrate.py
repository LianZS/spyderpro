import datetime

from spyderpro.port_connect.sqlconnect import MysqlOperation
from setting import *
from spyderpro.function.keywordfunction.mobilekey import MobileKey
from spyderpro.function.keywordfunction.searchkeyword import SearchKeyword

rootpath = os.path.dirname(os.path.abspath(os.path.pardir))
db = pymysql.connect(host=host, user=user, password=password, database='digitalsmart',
                     port=port)
cur = db.cursor()


class ManagerMobileKey(MobileKey, MysqlOperation):

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
        flag = 0
        for item in data:
            pid: int = item[0]
            area: str = item[1]
            flag: int = item[2]
            searcharea = search.key_check(area)  # 关键词纠正
            # baidu = search.baidu_browser_keyword_frequency(searcharea)  # 百度搜索
            #
            # if not baidu:
            #     continue
            # lastdate = self.last_date(pid, area, "baidu")  # 最近更新时间,0表示数据库里没有任何数据
            # for sql in self.sql_format(lastdate, baidu, pid, area, flag):
            #     try:
            #         cur.execute(sql)
            #     except Exception as e:
            #         print(area, e)
            #         db.rollback()
            #
            # db.commit()

            lastdate = 0
            month = 1
            year = 2016
            day = 1

            if area=='三明站' :
                flag=1
            if flag!=1:
                continue
            while 1:

                startdate = datetime.datetime(year, month, day)
                start = int(str(startdate.date()).replace("-", ""))

                enddate = datetime.datetime(year, month + 1, 1)
                end = int(str(enddate.date()).replace("-", ""))
                month += 1
                day = 2
                if month+1== 12:
                    month = 1
                    year += 1
                    continue
                if end > 20190901:
                    end = 20190820
                print(area, start, end)
                wechat = search.wechat_browser_keyword_frequency(searcharea, startdate=start,
                                                                 enddate=end)  # 只获取前2天的数据
                self.sumbit_commit(pid, area, lastdate, wechat, flag)

                sougou = search.sougou_browser_keyword_frequency(searcharea, startdate=start,
                                                                 enddate=end)  # 获取前两天的数据
                self.sumbit_commit(pid, area, lastdate, sougou, flag)
                if end == 20190820 :
                    break

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


#爬到了三明站 20170802 20170901
ManagerMobileKey().manager_search()