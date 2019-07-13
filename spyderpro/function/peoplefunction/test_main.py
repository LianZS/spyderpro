from spyderpro.function.peoplefunction.positioningtrend import PositioningTrend
from spyderpro.function.peoplefunction.positioningsituation import PositioningSituation
from spyderpro.function.peoplefunction.monitoring_area import PositioningPeople


def test1():
    PositioningPeople().get_the_scope_of_pace_data(start_lat=23.2, start_lon=110.2, end_lat=30.2, end_lon=113.2)


def test2():
    PositioningTrend().get_all_province()


def test3():
    PositioningTrend().get_all_place("广东省", "深圳市")


def test4():
    PositioningTrend().get_all_city("广东省")


def test5():
    PositioningTrend().get_place_index('深圳欢乐谷', 6, '2019-05-19', '2019-06-01')


def test6():
    PositioningSituation().get_count('2019-05-19', '10:15:00', 6)


def test7():
    PositioningSituation().get_distribution_situation('2019-05-19', '10:15:00', 6)


def test8():
    PositioningPeople().positioning_people_num(max_num=10)


if __name__ == "__main__":
    pass
