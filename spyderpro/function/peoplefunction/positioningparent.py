import re
from spyderpro.data_requests.locationdata.placepeople import PlaceTrend
from spyderpro.port_connect.sqlconnect import MysqlOperation


class PositiongParent(MysqlOperation):
    def get_all_province(self) -> list:
        """获取可以监测的省份
        :return 省份列表 [广东省，广西省.....]
        """
        place = PlaceTrend(date_begin=None, date_end=None)
        provinces = place.get_provinces()
        return provinces

    def get_all_city(self, province: str) -> list:
        """获取该省份下可以监测的城市
            :return 城市列表
        """
        assert re.match("\w{2,10}省$", province), 'the format of province is wrong ,the right format such as "广东省" '

        place = PlaceTrend(date_begin=None, date_end=None)
        citys = place.get_citys(province)
        return citys

    def get_all_place(self, province: str, city: str) -> list:
        """
          获取城市下所有景点信息

        :type province: str
        :type city:str
        :param province:省份
        :param city:城市

        :return: list[dict]
        get_all_place->list[{'place': '荔香公园', 'id': '18343'},,,,]
        """
        assert re.match("\w{2,10}省$", province) and re.match("\w{2,10}市$", city), \
            'the format of  param is wrong the right format such as "广东省,深圳市" '

        place = PlaceTrend(date_begin=None, date_end=None)
        datalist = place.get_regions_bycity(province, city)
        return datalist
