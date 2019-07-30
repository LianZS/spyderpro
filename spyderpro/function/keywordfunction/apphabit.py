from spyderpro.models.Internetdata.userhabit import UserHabit


class AppUserhabit:
    def get_user_portrait(self, year: int, startmonth: int, endmonth: int = None):
        """
        获取用户图像---性别分布 ，年龄分布，消费偏好，区域热度，应用偏好

        :param year: 2016<=year<2018
        :param startmonth:
        :param endmonth:
        :return:
        """
        data = UserHabit().get_user_portrait(year, startmonth, endmonth)
        return data

    def get_user_behavior(self, year: int, endmonth: int):
        """
        获取endmonth前5个月度用户行为---人均安装应用趋势，人均启动应用趋势
        """
        data = UserHabit().get_user_behavior(year, endmonth)
        return data

    def get_app_userhabit(self, appname: str, pid: int, start_date: str):
        """
        获取app的用户画像数据,性别占比,年龄分布,省份覆盖率,app用户关键词

        :param appname:
        :param start_date: 格式为yyyy-mm-dd
        :return:
        """

        data = UserHabit().get_app_userhabit(appname, pid, start_date)
        return data

    def get_app_active_data(self, appname, appid, start_date):
        """
        获取该app的月活跃数，活跃用户率，时间列表，行业基准，行业均值
        :param appname:app名字
        :param start_date:开始月份 ，如2019-01-01，注意，日必须是月首日
        :return:AppRateBenchmark
        :param appname:
        :param appid:
        :param start_date:
        :return:
        """
        data = UserHabit().get_app_active_info(appname, appid, start_date)
        return data
