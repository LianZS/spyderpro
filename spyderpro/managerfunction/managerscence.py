import datetime
from spyderpro.managerfunction.setting import *
from spyderpro.function.peoplefunction.posititioningscence import ScenceFlow
from spyderpro.function.peoplefunction.positioningtrend import PositioningTrend
from spyderpro.function.peoplefunction.positioningsituation import PositioningSituation
from spyderpro.function.peoplefunction.monitoring_area import PositioningPeople


class ManagerScence(ScenceFlow, PositioningTrend, PositioningSituation, PositioningPeople):

    def manager_scence_situation(self):
        """
        景区客流数据管理

        """
        db = pymysql.connect(host=host, user=user, password=password, database=scencedatabase,
                             port=port)
        instances = self.get_scence_situation(db=db, peoplepid=1174)
        for info in instances:
            sql = "insert into digitalsmart.scenceflow(pid, ddate, ttime, num) values ('%d','%d','%s','%d')" % (
                info.region_id, info.date, info.detailTime, info.num)
            self.write_data(db, sql)
        db.close()

    def manager_scence_trend(self):
        """
        地区人口趋势数据管理
        :return:
        """
        d = self.get_place_index(name='深圳欢乐谷', placeid=6, date_start='2019-07-18', date_end='2019-07-19')
        trend = d.__next__()
        print(trend.ddate,trend.place,trend.index,trend.detailtime)

    def manager_scenece_people_distribution(self):
        """
        地区人口分布数据管理
        :return:
        """
        db = pymysql.connect(host=host, user=user, password=password, database=scencedatabase,
                             port=port)
        instances = self.get_distribution_situation('2019-05-19', '10:15:00', 6)
        tmp_date = datetime.datetime(2019, 5, 19, 10, 15, 0).timestamp()

        for item in instances:
            sql = "insert into digitalsmart.peopleposition0(pid, tmp_date, lat, lon, num) VALUES" \
                  " ('%d','%d','%f','%f','%d')" % (6, tmp_date, item.latitude, item.longitude, item.number)
            self.write_data(db, sql)

    def manager_scenece_people_situation(self):
        """
        地区人口情况数据管理
        :return:

        """
        # time.strftime("%YYYY-%mm-%dd %HH:%MM:00",time.localtime())
        db = pymysql.connect(host=host, user=user, password=password, database=scencedatabase,
                             port=port)
        instance = self.get_count('2019-05-19', '10:15:00', 6)

        sql = "insert into digitalsmart.scenceflow(pid, ddate, ttime, num) values ('%d','%d','%s','%d')" % (
            instance.region_id, instance.date, instance.detailTime, instance.num)
        self.write_data(db, sql)

    def manager_china_positioning(self):
        """
        中国人定位数据管理
        :return:
        """
        instances = self.positioning_people_num(max_num=10)

    def manager_monitoring_area(self):
        """"""
        self.get_the_scope_of_pace_data(start_lat=23.2, start_lon=110.2, end_lat=30.2, end_lon=113.2)


ManagerScence().manager_scence_trend()
