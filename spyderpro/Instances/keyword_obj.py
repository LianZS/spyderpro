class KeyWordObject:
    __slots__ = ['all_value', 'pc_value', 'mobile_value', 'company', 'update']

    def __init__(self, company, all_value, pc, mobile, update):
        self.company = company  # 搜索引 擎
        self.all_value = all_value  # 全网频率
        self.pc_value = pc  # pc端频率
        self.mobile_value = mobile  # 移动端频率
        self.update = update  # 更新时间


class Mobile_Info:
    __slots__ = ['type_kw', 'type_name', 'value', 'date']

    def __init__(self, kw, type_name, value, date):
        self.type_kw = kw  # 大方向类型
        self.type_name = type_name  # 具体类型
        self.value = value  # 占有率
        self.date = date  # 日期
