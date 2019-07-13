import re
from spyderpro.function.peoplefunction.positioningparent import PositiongParent
from spyderpro.models.locationdata.placepeople import PlaceTrend


class PositioningTrend(PositiongParent):
    """
    位置流量趋势
    """

    def get_place_index(self, name: str, placeid: int, date_start: str, date_end: str):
        """
        获取地点某段时间的流量趋势指数
        :param name:地点
        :param placeid:id
        :param date_start:开始日期，日期：格式yyyy-mm-dd
        :param date_end:结束日期，日期：格式yyyy-mm-dd
        :return:iterable(dict)
        dict->{'place': '深圳欢乐谷', 'date': '2019-05-23', 'data': [0.19, 0.19, 0.1.....]}
        """

        assert re.match("\d{4}-\d{2}-\d{2}", date_start) and re.match("\d{4}-\d{2}-\d{2}", date_end), \
            "date format is wrong,please input the format such as '2019-06-12'"
        place = PlaceTrend(date_begin=date_start, date_end=date_end)
        data_iterable = place.get_trend(name, placeid)

        return data_iterable
