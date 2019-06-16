import pymysql
from spyderpro.Connect.MysqlConnect import MysqlOperation
from spyderpro.LocationBigData.PeopleNum import PeoplePositionin


class PeopleFucntion(MysqlOperation):
    def positioning_people_num(self, max_num: int = 8):
        """
        获取定位数据
        :param max_num:
        :return:
        """

        for rank in range(max_num):
            self.request_positioning_num(rank)

    def request_positioning_num(self, rank):
        positioning = PeoplePositionin()
        response = positioning.get_people_positionin_data(rank)

        for item in response:
            pass

    def __dealwith_positioning(self):
        """清空数据库，只保留目前爬去的数据"""
        pass

    def __get_the_scope_of_pace_data(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> list:
        """
        从数据中提取出在范围内的数据
        :param start_lat: 开始的纬度
        :param start_lon: 开始的经度
        :param end_lat: 结束的纬度
        :param end_lon: 结束的经度
        :return:list[[lat,lon]]
        """
        pass



PeopleFucntion().positioning_people_num()
