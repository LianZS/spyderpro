from spyderpro.function.trafficfunction.traffic import Traffic
from spyderpro.managerfunction.setting import *
from pymysql.connections import Connection


class ManagerTraffic(Traffic):
    def manager_city_traffic(self):
        db: Connection = pymysql.connect(host=host, user=user, password=password,
                                         database="digitalsmart",
                                         port=port)
        pid = 500000
        info = self.get_city_traffic(citycode=pid, db=db)
        if len(info) == 0:
            print("没有数据")
            return 0
        for item in info:
            date = item.date
            index = item.index
            detailtime = item.detailtime
            sql = "insert into  digitalsmart.citytraffic(pid, ddate, ttime, rate)" \
                  " values('%d', '%d', '%s', '%f');" % (
                      pid, date, detailtime, index)
            if not self.loaddatabase(db, sql):
                print("%s插入失败" % item)
                continue
        db.close()
        return 1


ManagerTraffic().manager_city_traffic()
