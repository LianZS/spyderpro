from spyderpro.managerfunction.setting import *
from spyderpro.function.scencefunction import ScenceFlow
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
        self.write_scence_situation(db, instances)

    def manager_scence_trend(self):
        """
        地区人口趋势数据管理
        :return:
        """
        self.get_place_index(name='深圳欢乐谷', placeid=6, date_start='2019-05-19', date_end='2019-06-01')

    def manager_scenece_people_distribution(self):
        """
        地区人口分布数据管理
        :return:
        """
        self.get_distribution_situation('2019-05-19', '10:15:00', 6)

    def manager_scenece_people_situation(self):
        """
        地区人口情况数据管理
        :return:

        """
        self.get_count('2019-05-19', '10:15:00', 6)

    def manager_china_positioning(self):
        """
        中国人定位数据管理
        :return:
        """
        self.positioning_people_num(max_num=10)

    def manager_monitoring_area(self):
        """"""
        self.get_the_scope_of_pace_data(start_lat=23.2, start_lon=110.2, end_lat=30.2, end_lon=113.2)


ManagerScence().manager_scence_situation()
