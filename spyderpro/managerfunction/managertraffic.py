from spyderpro.function.trafficfunction.traffic import Traffic
from spyderpro.managerfunction.setting import *
from pymysql.connections import Connection


class ManagerTraffic(Traffic):
    def manager_city_traffic(self):
        db: Connection = pymysql.connect(host=host, user=user, password=password,
                                         database="digitalsmart",
                                         port=port)
        pid = 3171
        info = self.get_city_traffic(citycode=pid, db=db)
        if len(info) == 0:
            print("没有数据")
            return 0
        for item in info:
            sql = "insert into  digitalsmart.citytraffic(pid, ddate, ttime, rate)" \
                  " values('%d', '%d', '%s', '%f');" % (
                      pid, item.date, item.detailtime, item.index)
            self.write_data(db, sql)
        db.close()
        return 1

    def manager_city_road_traffic(self):
        pid = 325
        self.road_manager(pid)

    def manager_city_year_traffic(self):
        pid = 500000
        self.yeartraffic(pid)  # 还未完善


ManagerTraffic().manager_city_year_traffic()
