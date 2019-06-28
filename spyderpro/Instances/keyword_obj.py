class KeyWordObject:
    __slots__ = ['all_value', 'pc_value', 'mobile_value', 'company', 'update']

    def __init__(self, company, all_value, pc, mobile, update):
        self.company = company
        self.all_value = all_value
        self.pc_value = pc
        self.mobile_value = mobile
        self.update = update
