class UserPortrait:
    """
    用户画像
    """
    __slots__ = ['ages', 'consumption', 'genders', 'preferences', 'provinces']

    def __init__(self, ages, consumption, genders, preferences, provinces):
        self.ages: map = ages  # 手机用户年龄段分布
        self.consumption: map = consumption  # 消费偏好
        self.genders: map = genders  # 性别分布
        self.preferences: map = preferences  # 应用偏好
        self.provinces: map = provinces  # 区域热度

    def __str__(self):
        return "手机用户年龄段分布:{0}\n消费偏好:{1}\n性别分布:{2}\n应用偏好:{3}\n区域热度:{4}".format(list(self.ages),
                                                                              list(self.consumption),
                                                                              list(self.genders),
                                                                              list(self.preferences),
                                                                              list(self.provinces))


class UserBehavior:
    """
    用户行为
     {"日期": date, "人均安装应用": install, "人均启动应用": active}
    """
    __slots__ = ['active_num', 'date', 'install']

    def __init__(self, active_num, install, date):
        self.active_num = active_num  # 人均启动应用
        self.install = install  # 人均安装应用
        self.date = date  # 日期

    def __str__(self):
        return "人均启动应用:{0},人均安装应用:{1},日期:{2}".format(self.active_num, self.install, self.date)


class AppRateBenchmark:
    """
    app画像
    """
    __slots__ = ['app_name', 'date', 'active_num', 'active_rate', 'rate_hight', 'rate_low']

    def __init__(self, name, date, active_num, active_rate, rate_hight, rate_low):
        self.app_name = name  # app名
        self.date = date  # 时间
        self.active_num = active_num  # 活跃用户数
        self.active_rate = active_rate  # 活跃用户率
        self.rate_hight = rate_hight  # 行业基准
        self.rate_low = rate_low  # 行业均值


class AppUserHabit:
    """
    app用户画像
    """
    __slots__ = ['app', 'age', 'gender', 'preference', 'province', 'ddate']

    def __init__(self, app, age, gender, preference, province, ddate):
        self.app = app
        self.age = age  # 性别占比列表
        self.gender = gender  # 年龄分布列表
        self.preference = preference  # app用户关键词列表
        self.province = province  # 省份覆盖率列表
        self.ddate = ddate  # 日期

    def __str__(self):
        return self.app + "日期：{4},性别占比列表:{0},年龄分布列表:{1},app用户关键词列表:{2},省份覆盖率列表:{3}".format(self.age, self.gender,
                                                                                    self.preference,
                                                                                    self.province,self.ddate)
