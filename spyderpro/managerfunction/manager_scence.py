from .setting import *
from spyderpro.function.scencefunction import People
from spyderpro.function.peopleflowfunction import People_Positioning, Positioning_Trend


class ManagerScence(People, People_Positioning, People_Positioning, Positioning_Trend):
    # @classmethod
    # def people_flow(cls, peoplepidlist):
    #     """
    #     获取人流数据
    #     :param peoplepidlist:id列表
    #     :return:
    #     """
    #     while True:
    #         if cls.instance is None:
    #             cls.instance = super().__new__(cls)
    #         cls.instance.programmerpool(cls.instance.getpeopleflow, peoplepidlist)
    def manager_scence_situation(self):
        """
        景区客流数据管理

        """
        db = pymysql.connect(host=host, user=user, password=password, database=scencedatabase,
                             port=port)
        instances = self.get_scence_situation(db=db, peoplepid=0)
        self.write_scence_situation(db, instances)

    def manager_scence_trend(self):
        """
        地区人口趋势
        :return:
        """
        pass

    def manager_scenece_people_distribution(self):
        """
        地区人口分布
        :return:
        """
        pass

    def manager_scenece_people_situation(self):
        """
        地区人口情况
        :return:
        """
        pass
