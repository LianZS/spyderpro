import re
from typing import Iterator
from spyderpro.data_instances.lbs import Trend
from spyderpro.function.people_function._positioning_parent import PositiongParent
from spyderpro.data_requests.scence.place_people_trend import PlaceTrend


class PositioningTrend(PositiongParent):
    """
    位置流量趋势
    """

    def get_place_index(self, name: str, placeid: int, date_start: str, date_end: str, predict: bool):
        """
        获取地点某段时间的流量趋势指数
        :param name:地点
        :param placeid:id
        :param date_start:开始日期，日期：格式yyyy-mm-dd
        :param date_end:结束日期，日期：格式yyyy-mm-dd
        :param predict：是否获取预测数据
        :return: Iterator[Trend]
        """

        assert re.match("\d{4}-\d{2}-\d{2}", date_start) and re.match("\d{4}-\d{2}-\d{2}", date_end), \
            "date format is wrong,please input the format such as '2019-06-12'"
        place = PlaceTrend(date_begin=date_start, date_end=date_end)
        trend_data: Iterator[Trend] = place.get_trend(name, placeid, predict)

        return trend_data
