import re
from spyderpro.function.people_function.positioningparent import PositiongParent
from spyderpro.data_requests.scence.place_people import PlaceTrend


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
        :return: Iterator[Trend]
        """

        assert re.match("\d{4}-\d{2}-\d{2}", date_start) and re.match("\d{4}-\d{2}-\d{2}", date_end), \
            "date format is wrong,please input the format such as '2019-06-12'"
        place = PlaceTrend(date_begin=date_start, date_end=date_end)
        data_iterable = place.get_trend(name, placeid)

        return data_iterable
