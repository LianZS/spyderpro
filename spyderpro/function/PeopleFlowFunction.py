import re
from concurrent import futures
from spyderpro.portconnect.MysqlConnect import MysqlOperation
from spyderpro.models.LocationBigData.PeopleNum import PeoplePositionin
from spyderpro.models.LocationBigData import PlaceTrend
from spyderpro.portconnect.ParamCheck import ParamTypeCheck


class People_Positioning(MysqlOperation, ParamTypeCheck):

    def positioning_people_num(self, max_num: int = 8):
        self.type_check(max_num, int)

        """
        获取定位数据
        :param max_num:
        :return:
        """
        executor = futures.ThreadPoolExecutor(max_workers=4)
        result = executor.map(self.request_positioning_num, range(max_num))
        for reponse in result:
            yield reponse

    def request_positioning_num(self, rank: int) -> list:

        self.type_check(rank, int)

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

    def get_the_scope_of_pace_data(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float):
        """
        从数据中提取出在范围内的数据
        :param start_lat: 开始的纬度
        :param start_lon: 开始的经度
        :param end_lat: 结束的纬度
        :param end_lon: 结束的经度
        :return:list[[lat,lon]]
        """


        self.type_check(start_lat,float)
        self.type_check(start_lon,float)
        self.type_check(end_lon,float)
        self.type_check(end_lat,float)

        result = self.positioning_people_num()
        count = 0
        for response in result:
            for data in response:
                lat = data[0]
                lon = data[1]
                num = data[2]
                if start_lat <= lat <= end_lat and start_lon <= lon <= end_lon:
                    count += num
        print(count)


class Place_Flow_Trend(MysqlOperation):
    """
    位置流量趋势
    """

    def get_all_province(self) -> list:
        """获取可以监测的省份
        :return 省份列表 [广东省，广西省.....]
        """
        place = PlaceTrend(date_begin=None, date_end=None)
        provinces = place.get_allprovince()
        return provinces

    def get_all_city(self, province: str) -> list:
        """获取该省份下可以监测的城市
            :return 城市列表
        """
        assert re.match("\w{2,10}省$", province), 'the format of province is wrong ,the right format such as "广东省" '

        place = PlaceTrend(date_begin=None, date_end=None)
        citys = place.get_allcity(province)
        return citys

    def get_all_place(self, province: str, city: str) -> list:
        """
          获取城市下所有景点信息

        :type province: str
        :type city:str
        :param province:省份
        :param city:城市

        :return: list[dict]
        dict->{'place': '荔香公园', 'id': '18343'}
        """
        assert re.match("\w{2,10}省$", province) and re.match("\w{2,10}市$", city), \
            'the format of  param is wrong the right format such as "广东省,深圳市" '

        place = PlaceTrend(date_begin=None, date_end=None)
        datalist = place.get_regions_bycity(province, city)
        return datalist

    def get_place_index(self, name: str, placeid: int, date_start: str, date_end: str):
        """
        获取地点某段时间的流量趋势指数
        :param name:地点
        :param placeid:id
        :param date_start:开始日期
        :param date_end:结束日期
        :return:iterable(dict)
        dict->{'place': '深圳欢乐谷', 'date': '2019-05-23', 'data': [0.19, 0.19, 0.1.....]}
        """

        assert re.match("\d{4}-\d{2}-\d{2}", date_start) and re.match("\d{4}-\d{2}-\d{2}", date_end), \
            "date format is wrong,please input the format such as '2019-06-12'"
        place = PlaceTrend(date_begin=date_start, date_end=date_end)
        data_iterable = place.getlocations(name, placeid)

        return data_iterable


if __name__ == "__main__":
    People_Positioning().get_the_scope_of_pace_data(start_lat=23.2, start_lon=110.2, end_lat=30.2, end_lon=113.2)
    Place_Flow_Trend().get_all_province()
    Place_Flow_Trend().get_all_place("广东省", "深圳市")
    Place_Flow_Trend().get_place_index('深圳欢乐谷', 6, '2019-05-19', '2019-06-01')
    Place_Flow_Trend().get_all_city("广东省")
