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
            yield self.request_positioning_num(rank)

    def request_positioning_num(self, rank) -> list:
        """
        请求定位数据
        :param rank:
        :return: list(data)->data:[纬度,经度,人数]
        """
        positioning = PeoplePositionin()
        response = positioning.get_people_positionin_data(rank)
        datalist = list()
        for item in response:
            data = list()
            data.append(item['纬度'])
            data.append(item['经度'])
            data.append(item['人数'])
            datalist.append(data)
        return datalist

    def __dealwith_positioning(self):
        """清空数据库，只保留目前爬去的数据"""
        pass

    def get_the_scope_of_pace_data(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> list:
        """
        从数据中提取出在范围内的数据
        :param start_lat: 开始的纬度
        :param start_lon: 开始的经度
        :param end_lat: 结束的纬度
        :param end_lon: 结束的经度
        :return:list[[lat,lon]]
        """
        result = self.positioning_people_num()
        count = 0
        for response in result:
            for data in response:
                lat = data[0]
                lon = data[1]
                num = data[2]
                if start_lat <= lat <= end_lat and start_lon <= lon <= end_lon:
                    count += num
        # print(count)

# PeopleFucntion().get_the_scope_of_pace_data(start_lat=23,start_lon=110,end_lat=30,end_lon=113)
