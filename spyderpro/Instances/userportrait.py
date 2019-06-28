class UserPortrait:
    __slots__ = ['ages', 'consumption', 'genders', 'preferences', 'provinces']

    def __init__(self, ages, consumption, genders, preferences, provinces):
        self.ages = ages  # 手机用户年龄段分布
        self.consumption = consumption  # 消费偏好
        self.genders = genders  # 性别分布
        self.preferences = preferences
        self.provinces = provinces  # 区域热度


class UserBehavior:
    __slots__ = ['active_num', 'date', 'install']

    def __init__(self, active_num, install, date):
        self.active_num = active_num  # 人均启动应用
        self.install = install  # 人均安装应用
        self.date = date  # 日期


class AppRateBenchmark:
    __slots__ = ['app_name', 'date', 'active_num', 'active_rate', 'rate_hight', 'rate_low']

    def __init__(self, name, date, active_num, active_rate, rate_hight, rate_low):
        self.app_name = name  # app名
        self.date = date  # 时间列表
        self.active_num = active_num  # 活跃用户数
        self.active_rate = active_rate  # 活跃用户率
        self.rate_hight = rate_hight  # 行业基准
        self.rate_low = rate_low  # 行业均值


class AppUserHabit:
    __slots__ = ['s']

    def __init__(self):
        pass
