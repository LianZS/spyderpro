import datetime
from typing import List
from spyderpro.managerfunction.redis_connect import RedisConnectPool
from spyderpro.managerfunction.mysql_connect import ConnectPool
from spyderpro.models.locationdata.scencepeople import ScencePeopleFlow
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

    def get_scence_situation(self, db, peoplepid, table_id) -> List[Positioning]:
        """
        请求某个景区实时客流量
        :param peoplepid: 景区id
        :return: bool
        """
        ddate: int = int(str(datetime.datetime.today().date()).replace("-", ''))
        flow = ScencePeopleFlow()
        # 获取数据
        instances = flow.peopleflow_info(peoplepid, ddate)
        # 缓冲数据
        positioning_data = list(instances)
        self.__redis_cache(positioning_data)#缓存数据
        # 过滤已存在的数据
        info = self.__filter_peopleflow(db, positioning_data, ddate, peoplepid, table_id)

        return info

    @staticmethod
    def __redis_cache(data_objs):
        """
        缓存数据,缓存key格式为 scence:pid
        :param data_objs: 数据实例
        :return:
        """
        dict_data = dict()  # {"HH:MM:SS":num}
        pid = 0
        for obj in data_objs:
            pid = obj.region_id
            detail_time = obj.detailTime
            num = obj.num
            dict_data[detail_time] = num
        redis_pool = RedisConnectPool(max_workers=1)
        key = "scence:{0}".format(pid)
        redis_pool.hashset(name=key, mapping=dict_data)

    # 检查数据库是否存在部分数据，存在则不再插入
    def __filter_peopleflow(self, db_connect, objs: List[Positioning], ddate: int, peoplepid: int, table_id: int) -> \
            List[Positioning]:
        """
        检查数据库是否存在部分数据，存在则不再插入
        :param db_connect:  数据库实例
        :param objs: Positioning列表
        :param ddate: 日期
        :param peoplepid: 数据库查询条件
        :return: list(Positioning)
        """
        sql_cmd = "select ttime from digitalsmart.historyscenceflow{table_id} where pid={pid} and  ddate={ddate} ".format(
            table_id=table_id, pid=peoplepid,
            ddate=ddate)
        cursor = self.get_cursor(db_connect, sql_cmd)  # 从数据库获取当天已存在的数据
        if cursor == "error":
            return []
        data = cursor.fetchall()  # 从数据库获取已经存在的数据

        cursor.close()
        dic = {}
        for info in objs:  # 构造对象字典
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


# class Weather(Parent):
#     @classmethod
#     def weather(cls, weatherpidlist):
#         """
#         获取天气数据
#         :param weatherpidlist: 天气id列表
#         :return:
#         """
#         while True:
#             if cls.instance is None:
#                 cls.instance = super().__new__(cls)
#             cls.instance.programmerpool(cls.instance.getweather, weatherpidlist)
#
#     # def getweather(self, weatherpid):
#     #     """
#     #     获取天气数据
#     #     :param weatherpid:
#     #     :return:
#     #     """
#     #     pool = ConnectPool(max_workers=1)
#     #     db = pymysql.connect(host=host, user=user, password=password, database=scencedatabase,
#     #                          port=port)
#     #
#     #     sql = "select WeatherTablePid from webdata.ScenceInfoData where  WeatherPid=" \
#     #           + "'" + weatherpid + "';"
#     #
#     #     cursor = self.get_cursor(db, sql)
#     #     if cursor is None:
#     #         return False
#     #     weathertablepid = cursor.fetchone()[0]
#     #     cursor.close()
#     #     wea = WeatherForect()
#     #     info = wea.weatherforcest(weatherpid)
#     #
#     #     # 每次爬取都是获取未来7天的数据，所以再次爬取时只需要以此刻为起点，看看数据库存不存在7天后的数据
#     #     date = time.strftime('%Y-%m-%d', time.localtime(
#     #         time.time() + 7 * 3600 * 24))
#     #     info = self.__dealwith_weather(info, db, weathertablepid, date)
#     #     for item in info:
#     #         date = item['date']
#     #         detailtime = item['detailTime']
#     #         state = item['state']
#     #         temperature = item['temperature']
#     #         wind = item['wind']
#     #         sql = "insert into  webdata.weather(pid_id,date,detailTime,state,temperature,wind) " \
#     #               "values('%d','%s','%s','%s','%s','%s');" % (
#     #                   weathertablepid, date, detailtime, state, temperature, wind)
#     #         if not self.loaddatabase(db, sql):
#     #             print("插入失败！")
#     #             continue
#     #
#     #     db.close()
#     #     print("success")
#     #     return True
#
#     # 有bug
#     def __dealwith_weather(self, info, db, pid, date) -> list:
#         """
#         过滤已存在天气数据
#         :param info:
#         :param db:
#         :param pid:
#         :param date:
#         :return:list
#         """
#
#         sql = "select  date,detailTime from webdata.weather where pid_id=" + str(
#             pid) + " and date =str_to_date('" + date + "','%Y-%m-%d');"
#         cursor = self.get_cursor(db, sql)
#         if cursor is None:
#             cursor.close()
#             return info
#         data = cursor.fetchall()
#
#         if len(data) == 0:
#             cursor.close()
#             return info
#         lis = []
#
#         for item in info:
#             if item['date'] != date:
#                 continue
#             lis.append(dict(zip(item.values(), item.keys())))
#         info = lis
#         for olddata in data:
#             self.filter(info, olddata[0], olddata[1])
#         lis = []
#         for item in info:
#             lis.append(dict(zip(item.values(), item.keys())))
#         info = lis
#         return info


if __name__ == "__main__":
    p = ScenceFlow()
    pool = ConnectPool(max_workers=1)
    db = pool.work_queue.get()
    p.get_scence_situation(db, 1365,555)
    # db = pymysql.connect(host=host, user=user, password=password, database=scencedatabase,
    #                      port=port)
    # data = p.get_scence_situation(db, 1174)
    # #
    # p.write_scence_situation(db, data)
