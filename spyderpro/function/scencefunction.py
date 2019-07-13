import time
import csv

from spyderpro.models.locationdata.scencepeople import ScencePeopleFlow
from spyderpro.models.weather.weather import WeatherForect
from spyderpro.models.traffic import baidutraffic
from spyderpro.models.traffic import gaodetraffic

from concurrent.futures import ThreadPoolExecutor
from spyderpro.managerfunction.setting import *
from spyderpro.portconnect.sqlconnect import MysqlOperation
from spyderpro.instances.lbs import Positioning


class Parent(MysqlOperation):

    @staticmethod
    def initdatabase():
        """
        录入数据库景区数据库信息
        :return:
        """
        db = pymysql.connect(host=host, user=user, password=password, database=scencedatabase,
                             port=port)
        db.connect()
        cursor = db.cursor()
        with open(scencefilepath, 'r') as f:
            reader = csv.reader(f)
            reader.__next__()  # 跳过表头
            count = 0
            for item in reader:
                count += 1
                name = str(item[0]).strip(' ')
                peoplepid = int(item[1])
                bounds_lon = float(item[2])
                bounds_lat = float(item[3])
                citycode = int(item[4])
                weatherpid = str(item[5]).strip(" ")
                peopletablepid = count
                citytablecode = count
                weathertablepid = count

                sql = "insert into webdata.ScenceInfoData(name,bounds_lon,bounds_lat,PeoplePid,CityCode,WeatherPid," \
                      "PeopleTablePid,CityTableCode,WeatherTablePid)" \
                      " values ('%s','%f','%f','%d','%d','%s','%d','%d','%d')" % (
                          name, bounds_lon, bounds_lat, peoplepid, citycode, weatherpid, peopletablepid, citytablecode,
                          weathertablepid)
                try:
                    cursor.execute(sql)
                    db.commit()
                except Exception as e:
                    print("error:%s" % e)
                    db.rollback()
        cursor.close()
        db.close()
        return True

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
    def filter(info, date, detailtime):
        for i in range(len(info)):
            if info[i].get(str(date)) and info[i].get(detailtime):
                info.pop(i)
                return


class People(Parent):

    def write_scence_situation(self, db, objs) -> bool:
        """
        数据库写入
        :param db:
        :param objs:
        :return:
        """
        for info in objs:
            sql = "insert into peopleFlow(pid_id,date,num,detailTime) values ('%d','%s','%d','%s');" % (
                info.region_id, info.date, info.num, info.detailTime)
            if not self.loaddatabase(db, sql):
                print("插入出错")
                continue

        db.close()
        return True

    def get_scence_situation(self, db, peoplepid):
        """
        请求某个景区实时客流量
        :param peoplepid: 景区id
        :return: bool
        """
        date = time.strftime('%Y-%m-%d', time.localtime())
        flow = ScencePeopleFlow()
        instances = flow.peopleflow_info(peoplepid, date)

        info = self.__filter_peopleflow(db, instances, date, peoplepid)

        return info

    # 检查数据库是否存在部分数据，存在则不再插入
    def __filter_peopleflow(self, db, objs, date, peoplepid) -> list:
        """
        检查数据库是否存在部分数据，存在则不再插入
        :param db:  数据库实例
        :param info: Positioning迭代器
        :param date: 日期
        :param peopletablepid: 数据库查询条件
        :return: list(Positioning)
        """

        sql = "select detailTime from webdata.peopleFlow where  pid_id=" + str(
            peoplepid) + " and  date=str_to_date('" + str(date) + "','%Y-%m-%d');"
        cursor = self.get_cursor(db, sql)
        if cursor is None:
            return []
        data = cursor.fetchall()  # 从数据库获取已经存在的数据
        cursor.close()
        dic = {}
        for info in objs:
            dic[info.detailTime] = info

        for item in data:  # 将存在的数据淘汰掉
            try:
                dic.pop(item[0])
            except KeyError:
                continue
        return list(dic.values())
        # for detailTime, num in dic.items():  # 因为过滤后的数据少，所以直接新实例化对象，增强可读性
        #     yield Positioning(region_id=peoplepid, date=date, detailtime=detailTime, num=num)


class Traffic(Parent):
    @classmethod
    def traffic(cls, citycodelist):
        """
        获取交通情况
        :param citycodelist:
        :return:
        """
        while True:
            if cls.instance is None:
                cls.instance = super().__new__(cls)
            cls.instance.programmerpool(cls.instance.gettraffic, citycodelist)

    def gettraffic(self, citycode) -> bool:
        """
        请求交通数据
        :param citycode:
        :return:
        """
        db = pymysql.connect(host=host, user=user, password=password, database=scencedatabase,
                             port=port)

        sql = "select CityTableCode from webdata.ScenceInfoData where  CityCode=" + "'" + str(citycode) + "';"

        cursor = self.get_cursor(db, sql)
        if cursor is None:
            print("cursor is None")
            return False
        citytablecode = cursor.fetchone()[0]
        cursor.close()

        if citycode > 1000:
            traffic = gaodetraffic()

        elif 0 < citycode < 1000:
            traffic = baidutraffic()

        else:
            return False
        t = time.time()

        today = time.strftime('%Y-%m-%d', time.localtime(t))
        yesterday = time.strftime('%Y-%m-%d', time.localtime(t - 3600 * 24))
        info = traffic.citytraffic(citycode)

        info = self.__dealwith_traffic(info, db, citytablecode, today, yesterday)
        if info is None:
            print("Null")
            return False

        for item in info:
            date = item['date']
            index = float(item['index'])
            detailtime = item['detailTime']
            sql = "insert into  webdata.traffic(pid_id,date,TrafficIndex,detailTime) " \
                  "values('%d','%s','%s','%s');" % (
                      citytablecode, date, index, detailtime)
            self.loaddatabase(db, sql)

        print("success")
        db.close()
        return True

    def __dealwith_traffic(self, info, db, pid, today, yesterday):

        lis = []
        for item in info:
            lis.append(dict(zip(item.values(), item.keys())))
        info = lis
        # 将昨天的数据全部剔除
        for i in range(len(info)):
            if info[i].get(yesterday) is None:
                info = info[i + 1:]
                break

        sql = "select  date,detailTime from webdata.traffic where pid_id=" + str(
            pid) + " and date =str_to_date('" + today + "','%Y-%m-%d');"
        cursor = self.get_cursor(db, sql)
        if cursor is None:
            return
        data = cursor.fetchall()
        cursor.close()
        # 剔除今天重复的数据
        for item in data:
            self.filter(info, item[0], item[1])
        lis.clear()
        for item in info:
            lis.append(dict(zip(item.values(), item.keys())))
        info = lis
        return info


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
    p = People()

    db = pymysql.connect(host=host, user=user, password=password, database=scencedatabase,
                         port=port)
    data = p.get_scence_situation(db, '1174')

    p.write_scence_situation(db, data)
