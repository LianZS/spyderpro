from spyderpro.function.keywordfunction.mobilekey import MobileKey


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


if __name__ == "__main__":
    pass
