import datetime
import time
import json
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from spyderpro.managerfunction.mysql_connect import ConnectPool
from spyderpro.managerfunction.redis_connect import RedisConnectPool
from spyderpro.function.peoplefunction.posititioningscence import ScenceFlow
from spyderpro.function.peoplefunction.positioningtrend import PositioningTrend
from spyderpro.function.peoplefunction.positioningsituation import PositioningSituation
from spyderpro.function.peoplefunction.monitoring_area import PositioningPeople


class ManagerScence(ScenceFlow, PositioningTrend, PositioningSituation, PositioningPeople):

    def __init__(self):
        self.redis_obj = RedisConnectPool(max_workers=10)



    def manager_scence_situation(self):
        """
        景区客流数据管理----半小时一轮

        """
        # 接连接池
        pool = ConnectPool(max_workers=10)
        sql = "select ds.pid,dt.table_id from digitalsmart.scencemanager as ds inner join digitalsmart.tablemanager " \
              "as dt on ds.type_flag=dt.flag   and ds.pid=dt.pid where ds.type_flag=1"
        iterator_pids = pool.select(sql)
        # 防止并发太多
        thread_pool = ThreadPoolExecutor(max_workers=10)
        for pid, table_id in iterator_pids:
            def fast(area_id, table_index):
                """

                :param area_id: 景区id
                :param table_index: 景区所处表序号
                :return:
                """
                db2 = pool.work_queue.get()
                instances = self.get_scence_situation(db=db2, peoplepid=area_id, table_id=table_index)
                pool.work_queue.put(db2)
                sql_format = "insert into digitalsmart.historyscenceflow{0}(pid, ddate, ttime, num) " \
                             "values ('%d','%d','%s','%d')".format(table_index)
                for info in instances:
                    sql_cmd = sql_format % (
                        info.region_id, info.date, info.detailTime, info.num)
                    # 提交
                    pool.sumbit(sql_cmd)

            thread_pool.submit(fast, pid, table_id)

        print("百度资源景区数据挖掘完毕")

    def manager_scence_trend(self):
        """
        地区人口趋势数据管理---5分钟一次
        :return:
        """

        # 今天
        date_today = datetime.datetime.today()
        # 时间间隔
        time_inv = datetime.timedelta(days=1)
        # 明天
        date_tomorrow = date_today + time_inv
        # 今天日期
        str_start = str(date_today.date())

        # 结束日期
        str_end = str(date_tomorrow.date())
        pool = ConnectPool(10)

        sql = "select pid,area from digitalsmart.scencemanager where type_flag=0 "
        data = pool.select(sql)
        thread_pool = ThreadPoolExecutor(max_workers=10)
        for item in data:

            pid = item[0]
            area = item[1]

            def fast(region_id, place):
                # 最近的更新时间
                sql_cmd = "select ttime from digitalsmart.scencetrend where pid={0} and ddate='{1}' " \
                          "order by ttime".format(region_id, int(str_start.replace("-", "")))
                last_ttime = "-1:00:00"  # 默认-1点

                try:
                    # 最近时间
                    table_last_time = pool.select(sql_cmd)[-1][0]
                    last_ttime = str(table_last_time)
                except IndexError:
                    pass
                # 获取趋势数据
                result_objs = self.get_place_index(name=place, placeid=region_id, date_start=str_start,
                                                   date_end=str_end)
                for obj in result_objs:
                    ttime = obj.detailtime
                    if ttime <= last_ttime:
                        continue

                    region_id = obj.region_id
                    ddate = obj.ddate
                    rate = obj.index
                    sql_cmd = "insert into digitalsmart.scencetrend(pid, ddate, ttime, rate) VALUE(%d,%d,'%s',%f)" % (
                        region_id, ddate, ttime, rate)
                    pool.sumbit(sql_cmd)

            thread_pool.submit(fast, pid, area)
        print("景区趋势挖掘完毕")

    def manager_scenece_people(self):
        """
        某时刻的人流
        :return:
        """
        self.pool = ConnectPool(10)
        up_date = int(datetime.datetime.now().timestamp())
        sql_cmd = "select pid,latitude,longitude from digitalsmart.scencemanager where type_flag=0"

        data = self.pool.select(sql_cmd)

        date_today = datetime.datetime.today()
        ddate = str(date_today.date())
        tmp_date = date_today.timestamp()  # 更新时间
        if date_today.time().minute % 5 > 0:  # 纠正计算挤时间，分钟必须事5的倍数
            now_time = date_today.time()
            minute = now_time.minute - now_time.minute % 5
            detailtime = "{0:0>2}:{1:0>2}:00".format(now_time.hour, minute)
        else:
            detailtime = time.strftime("%H:%M:00", time.localtime(tmp_date))
        thread_pool = ThreadPoolExecutor(max_workers=10)
        for info in data:

            def fast(item):
                region_id = item[0]
                float_lat = item[1]
                float_lon = item[2]

                sql_cmd = "select table_id from digitalsmart.tablemanager where pid={0}".format(region_id)
                # 数据对应在哪张表插入
                table_id = self.pool.select(sql_cmd)[0][0]
                last_people_data = self.get_data(date=ddate, dateTime=detailtime, region_id=region_id)
                if not last_people_data:
                    return
                Thread(target=self.manager_scenece_people_distribution,
                       args=(last_people_data, region_id, up_date, float_lat, float_lon, table_id)).start()
                self.manager_scenece_people_situation(table_id, last_people_data, region_id, ddate, detailtime)

            thread_pool.submit(fast, info)
        print("景区人流数据挖掘完毕")

    def manager_scenece_people_distribution(self, data, region_id, tmp_date: int, centerlat: float, centerlon: float,
                                            table_id: int):
        """
        地区人口分布数据---这部分每次有几k条数据插入
        :return:
        """
        # 获取经纬度人数结构体迭代器
        instances = self.get_distribution_situation(data)
        # 确定哪张表
        select_table = "insert into digitalsmart.peopleposition{0} (pid, tmp_date, lat, lon, num) VALUES".format(
            table_id)
        # 存放经纬度人数数据
        list_data = list()
        redis_data = list()  # 缓存列表
        for item in instances:
            list_data.append(
                str((region_id, tmp_date, centerlat + item.latitude, centerlon + item.longitude, item.number)))
            redis_data.append([{"latitude": centerlat + item.latitude}, {"longitude": centerlon + item.longitude},
                               {"num": item.number}])
        # 一条条提交到话会话很多时间在日志生成上，占用太多IO了，拼接起来再写入，只用一次日志时间而已
        # 但是需要注意的是，一次性不能拼接太多，管道大小有限制---需要在MySQL中增大Max_allowed_packet，否则会报错
        redis_key = "distribution:{0}".format(region_id)  # 缓存key
        # 缓存待定
        value = json.dumps(redis_data)

        self.redis_obj.set(name=redis_key, value=value)
        if len(list_data) > 20000:
            # 拆分成几次插入
            count: int = int(len(list_data) / 20000)
            i = 0
            # 切分插入
            for i in range(count):
                # 数据拆分
                slice_data = list_data[i * 20000:(i + 1) * 20000]
                sql_value = ','.join(slice_data)
                sql = select_table + sql_value
                self.pool.sumbit(sql)
            slice_data = list_data[(i + 1) * 20000:]
            sql_value = ','.join(slice_data)
            sql = select_table + sql_value
            self.pool.sumbit(sql)

        else:
            sql_value = ','.join(list_data)

            sql = select_table + sql_value
            self.pool.sumbit(sql)
        # 更新人流分布管理表的修改时间
        sql = "update digitalsmart.tablemanager  " \
              "set last_date={0} where pid={1}".format(tmp_date, region_id)
        self.pool.sumbit(sql)

    def manager_scenece_people_situation(self, table_id, data, pid, date, ttime):
        """
        地区人口情况数据  ---这部分每次只有一条数据插入
        """

        instance = self.get_count(data, date, ttime, pid)
        sql_format = "insert into digitalsmart.historyscenceflow{0}(pid, ddate, ttime, num)  " \
                     "values (%d,%d,'%s',%d) ".format(
            table_id)
        sql = sql_format % (
            instance.region_id, instance.date, instance.detailTime, instance.num)
        self.pool.sumbit(sql)

    # def manager_history_sceneceflow(self):
    #     """
    #     将昨天的数据存放到历史记录表里
    #     :return:
    #     """
    #     inv = datetime.timedelta(days=1)
    #     today = datetime.datetime.today()
    #     yesterday = int(str((today - inv).date()).replace("-", ""))
    #
    #     sql = "select pid,table_id from digitalsmart.tablemanager"
    #     pool = ConnectPool(max_workers=10)
    #     result = pool.select(sql)
    #     if not result:
    #         return None
    #
    #     def fast(data, histtory_table_id):
    #         if not data:
    #             return None
    #
    #         sql_format = "insert into digitalsmart.historyscenceflow{0}(pid, ddate, ttime, num) VALUES".format(
    #             histtory_table_id)
    #         # 将元祖元素转为字符串
    #         list_data = list()
    #         for item in data:
    #             list_data.append(str((item[0], item[1], str(item[2]), item[3])))
    #         # 拼接字符串
    #         sql = sql_format + ','.join(list_data)
    #         # 写入
    #         pool.sumbit(sql)
    #
    #     thread_pool = ThreadPoolExecutor(max_workers=10)
    #     for pid, table_id in result:
    #         sql = "select pid,ddate,ttime,num from digitalsmart.scenceflow where pid={0} and ddate={1} ".format(pid,
    #                                                                                                             yesterday)
    #         yesterday_info = pool.select(sql)
    #         thread_pool.submit(fast, yesterday_info, table_id)
    #     print("昨日数据写入历史记录表成功")

    def manager_china_positioning(self):
        """
        中国人定位数据管理---待完善
        :return:
        """
        instances = self.positioning_people_num(max_num=10)

    def manager_monitoring_area(self):
        """"""
        self.get_the_scope_of_pace_data(start_lat=23.2, start_lon=110.2, end_lat=30.2, end_lon=113.2)

    # def clear_sceneflow_table(self):
    #     sql = "truncate table digitalsmart.scenceflow"
    #     pool = ConnectPool(max_workers=1)
    #     pool.sumbit(sql)
    #
    # def clear_peopleposition_table(self):
    #     # 清空peoplepositionN人口密度分布表
    #     pass

    # for i in range(10):
    #
    #     sql = "truncate table digitalsmart.peopleposition{0}".format(i)
    #     try:
    #         cur.execute(sql)
    #         db.commit()
    #     except Exception:
    #         db.rollback()


ManagerScence().manager_scenece_people()
