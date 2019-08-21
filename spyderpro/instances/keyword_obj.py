from typing import Iterator


class BaiduKeyWordObject:
    __slots__ = ['all_value', 'pc_value', 'mobile_value', 'company', 'update']

    def __init__(self, company, all_value, pc, mobile, update):
        self.company: str = company  # 搜索引擎
        self.all_value: Iterator = all_value  # 全网频率
        self.pc_value: Iterator = pc  # pc端频率
        self.mobile_value: Iterator = mobile  # 移动端频率
        self.update: int = int(update)  # 更新时间

    def __str__(self):
        return "搜索引擎:{0},全网频率:{1},pc端频率:{2},移动端频率:{3},更新时间:{3}".format(self.company, self.all_value, self.pc_value,
                                                                       self.mobile_value, self.update)


class WechatKeyWordObject:
    __slots__ = ['company', 'all_value', 'update']

    def __init__(self, company: str, all_value: int, update: int):
        self.company: str = company
        self.all_value: int = all_value
        self.update: int = update

    def __str__(self):
        return "搜索引擎:{0},全网频率:{1},更新时间:{2}".format(self.company, self.all_value, self.update)


class SougouKeyWordObject:
    __slots__ = ['company', 'all_value', 'update']

    def __init__(self, company: str, all_value: int, update: int):
        self.company: str = company
        self.all_value: int = all_value
        self.update: int = update

    def __str__(self):
        return "搜索引擎:{0},全网频率:{1},更新时间:{2}".format(self.company, self.all_value, self.update)


class Mobile_Info:
    __slots__ = ['type_kw', 'type_name', 'value', 'date']

    def __init__(self, kw, type_name, value, date):
        self.type_kw = kw  # 大方向类型
        self.type_name = type_name  # 具体类型
        self.value = value  # 占有率
        self.date = date  # 日期
