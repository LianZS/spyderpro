from spyderpro.function.keyword_function.mobilekey import MobileKey
from spyderpro.function.keyword_function.searchkeyword import SearchKeyword


def test1():
    s = MobileKey()
    s.request_mobile_brand_rate(2018, 1, 2)


def test2():
    s = MobileKey()
    s.request_mobile_network_rate(2018, 1, 2)


def test3():
    s = MobileKey()
    s.request_mobile_operator_rate(2018, 1, 2)


def test4():
    s = MobileKey()
    s.request_mobile_system_rate(2018, 1, 2)


def test5():
    s = MobileKey()
    s.request_mobile_type_rate(2018, 1, 2)


def test6():
    SearchKeyword().browser_keyword_frequency("python")


if __name__ == "__main__":
    pass
