import json
from spyderpro.function.peoplefunction.positioningparent import PositiongParent
from spyderpro.models.locationdata.placepeople import PlaceFlow


class PositioningSituation(PositiongParent):

    def get_data(self, date: str, dateTime: str, region_id: int) -> json:
        """
        获取json数据
      :param date:日期：格式yyyy-mm-dd
        :param dateTime:时间：格式hh:MM:SS
        :param region_id:地区唯一表示
        :return:
        """
        p = PlaceFlow()
        response = p.get_heatdata_bytime(date, dateTime, region_id)
        return response

    def get_count(self, data: json, date: str, dateTime: str, region_id: int):
        """
        某一时刻的人数有多少
        :param date:日期：格式yyyy-mm-dd
        :param dateTime:时间：格式hh:MM:SS
        :param region_id:地区唯一表示

        """
        p = PlaceFlow()
        data_obj = p.count_headdata(data, date, dateTime,
                                    region_id)
        return data_obj

    def get_distribution_situation(self, data: json):
        """
        某一时刻的人数以及分布情况
           :param date:日期：格式yyyy-mm-dd
           :param dateTime:时间：格式hh:MM:SS
           :param region_id:地区唯一表示

        """
        p = PlaceFlow()
        data_obj = p.complete_headata(data)
        return data_obj
