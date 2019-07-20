import time
import datetime
from typing import List
from setting import *
from spyderpro.models.locationdata.scencepeople import ScencePeopleFlow
from spyderpro.models.weather.weather import WeatherForect
from concurrent.futures import ThreadPoolExecutor
from spyderpro.portconnect.sqlconnect import MysqlOperation

from spyderpro.instances.lbs import Positioning


class Parent(MysqlOperation):

    @staticmethod
    def programmerpool(func, pidlist):
        tasklist = []

        threadpool = ThreadPoolExecutor(max_workers=6)

        for pid in pidlist:
            task = threadpool.submit(func, pid)
            tasklist.append(task)
        while [item.done() for item in tasklist].count(False):
            pass

    '''过滤器'''

    @staticmethod
    def filter(info, date, detailtime) -> List[Positioning]:
        for i in range(len(info)):
            if info[i].get(str(date)) and info[i].get(detailtime):
                info.pop(i)
                break
        return info


class ScenceFlow(Parent):

    def get_scence_situation(self, db, peoplepid) -> List[Positioning]:
        """
        请求某个景区实时客流量
        :param peoplepid: 景区id
        :return: bool
        """
        # date = time.strftime('%Y-%m-%d', time.localtime())
        ddate: int = int(str(datetime.datetime.today().date()).replace("-", ''))
        flow = ScencePeopleFlow()
        instances = flow.peopleflow_info(peoplepid, ddate)

        info = self.__filter_peopleflow(db, instances, ddate, peoplepid)

        return info

    # 检查数据库是否存在部分数据，存在则不再插入
    def __filter_peopleflow(self, db, objs, ddate: int, peoplepid: int) -> List[Positioning]:
        """
        检查数据库是否存在部分数据，存在则不再插入
        :param db:  数据库实例
        :param objs: Positioning迭代器
        :param ddate: 日期
        :param peoplepid: 数据库查询条件
        :return: list(Positioning)
        """

        sql = "select ttime from digitalsmart.scenceflow where pid={0} and  ddate={1} ".format(peoplepid,
                                                                                               ddate)
        cursor = self.get_cursor(db, sql)  # 从数据库获取当天已存在的数据
        if cursor == "error":
            return []
        data = cursor.fetchall()  # 从数据库获取已经存在的数据

        cursor.close()
        dic = {}
        for info in objs:
            dic[info.detailTime] = info

        for item in data:  # 将存在的数据淘汰掉
            item = str(item[0])
            # 因为从数据库取出来数据时不知为什么变为 、 0：00：00这种格式不适合
            detailtime: str = item if len(item) == 8 else "0" + item
            try:
                dic.pop(detailtime)
            except KeyError:
                continue

        return list(dic.values())
        # for detailTime, num in dic.items():  # 因为过滤后的数据少，所以直接新实例化对象，增强可读性
        #     yield Positioning(region_id=peoplepid, date=date, detailtime=detailTime, num=num)




class Weather(Parent):
    @classmethod
    def weather(cls, weatherpidlist):
        """
        获取天气数据
        :param weatherpidlist: 天气id列表
        :return:
        """
        while True:
            if cls.instance is None:
                cls.instance = super().__new__(cls)
            cls.instance.programmerpool(cls.instance.getweather, weatherpidlist)

    def getweather(self, weatherpid):
        """
        获取天气数据
        :param weatherpid:
        :return:
        """
        db = pymysql.connect(host=host, user=user, password=password, database=scencedatabase,
                             port=port)

        sql = "select WeatherTablePid from webdata.ScenceInfoData where  WeatherPid=" \
              + "'" + weatherpid + "';"

        cursor = self.get_cursor(db, sql)
        if cursor is None:
            return False
        weathertablepid = cursor.fetchone()[0]
        cursor.close()
        wea = WeatherForect()
        info = wea.weatherforcest(weatherpid)

        # 每次爬取都是获取未来7天的数据，所以再次爬取时只需要以此刻为起点，看看数据库存不存在7天后的数据
        date = time.strftime('%Y-%m-%d', time.localtime(
            time.time() + 7 * 3600 * 24))
        info = self.__dealwith_weather(info, db, weathertablepid, date)
        for item in info:
            date = item['date']
            detailtime = item['detailTime']
            state = item['state']
            temperature = item['temperature']
            wind = item['wind']
            sql = "insert into  webdata.weather(pid_id,date,detailTime,state,temperature,wind) " \
                  "values('%d','%s','%s','%s','%s','%s');" % (
                      weathertablepid, date, detailtime, state, temperature, wind)
            if not self.loaddatabase(db, sql):
                print("插入失败！")
                continue

        db.close()
        print("success")
        return True

    # 有bug
    def __dealwith_weather(self, info, db, pid, date) -> list:
        """
        过滤已存在天气数据
        :param info:
        :param db:
        :param pid:
        :param date:
        :return:list
        """

        sql = "select  date,detailTime from webdata.weather where pid_id=" + str(
            pid) + " and date =str_to_date('" + date + "','%Y-%m-%d');"
        cursor = self.get_cursor(db, sql)
        if cursor is None:
            cursor.close()
            return info
        data = cursor.fetchall()

        if len(data) == 0:
            cursor.close()
            return info
        lis = []

        for item in info:
            if item['date'] != date:
                continue
            lis.append(dict(zip(item.values(), item.keys())))
        info = lis
        for olddata in data:
            self.filter(info, olddata[0], olddata[1])
        lis = []
        for item in info:
            lis.append(dict(zip(item.values(), item.keys())))
        info = lis
        return info


if __name__ == "__main__":
    p = ScenceFlow()

    # db = pymysql.connect(host=host, user=user, password=password, database=scencedatabase,
    #                      port=port)
    # data = p.get_scence_situation(db, 1174)
    # #
    # p.write_scence_situation(db, data)
