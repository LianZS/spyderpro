import datetime
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
        db: Connection = pymysql.connect(host=host, user=user, password=password,
                                         database="digitalsmart",
                                         port=port)

        up_date = datetime.datetime.now().timestamp()
        pid = 500000

        for item in self.road_manager(pid):  # 速度需要使用高并发加快速度
            sql = "insert into digitalsmart.roadtraffic(pid, roadname, up_date, speed, direction, bound, data) VALUE" \
                  "(%d,'%s',%d,%f,'%s','%s','%s') " % (
                      item.region_id, item.roadname, up_date, item.speed, item.direction, item.bounds,
                      item.data)
            self.write_data(db, sql)

    def manager_city_year_traffic(self):
        db: Connection = pymysql.connect(host=host, user=user, password=password,
                                         database="digitalsmart",
                                         port=port)

        pid = 317
        for item in self.yeartraffic(pid):
            pid = item.region_id
            date = item.date
            index = item.index
            sql = "insert into digitalsmart.yeartraffic(pid, tmp_date, rate) VALUE (%d,%d,%f)" % (pid, date, index)
            self.write_data(db,sql)


ManagerTraffic().manager_city_year_traffic()
