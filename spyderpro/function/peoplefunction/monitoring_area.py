from spyderpro.port_connect.paramchecks import ParamTypeCheck
from spyderpro.port_connect.sqlconnect import MysqlOperation
from spyderpro.data_requests.locationdata.positioning import PeoplePositionin


class PositioningPeople(MysqlOperation, ParamTypeCheck):

    def positioning_people_num(self, max_num: int = 10):
        self.type_check(max_num, int)

        """
        获取定位数据
        :param max_num:
        :return:
        """
        for rank in range(max_num):
            response = self.request_positioning_num(rank)
            yield response

    def request_positioning_num(self, rank: int) -> list:

        self.type_check(rank, int)

        """
        请求定位数据
        :param rank:
        :return: iter(Geographi....)
        """
        positioning = PeoplePositionin()
        response = positioning.get_people_positionin_data(rank, max_num=10)
        # datalist = list()
        # for item in response:
        #     data = list()
        #     data.append(item['纬度'])
        #     data.append(item['经度'])
        #     data.append(item['人数'])
        #     datalist.append(data)
        return response

    def __dealwith_positioning(self):
        """清空数据库，只保留目前爬去的数据"""
        pass

    def get_the_scope_of_pace_data(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float):
        """
        从数据中提取出在范围内的数据
        :param start_lat: 开始的纬度
        :param start_lon: 开始的经度
        :param end_lat: 结束的纬度
        :param end_lon: 结束的经度
        :return:list[[lat,lon]]
        """

        self.type_check(start_lat, float)
        self.type_check(start_lon, float)
        self.type_check(end_lon, float)
        self.type_check(end_lat, float)

        result = self.positioning_people_num(max_num=10)
        count = 0
        # 下面必须使用高并发来计算---待完善
        for response in result:
            for info in response:
                lat = info.latitude
                lon = info.longitude
                num = info.number
                if start_lat <= lat <= end_lat and start_lon <= lon <= end_lon:
                    count += num
        return count
