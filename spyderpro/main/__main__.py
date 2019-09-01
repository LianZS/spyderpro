import sys
import os
import time
import datetime
#
# sys.path[1] = '/root/SpyderPr'
# sys.path[0] = os.path.abspath(os.path.join(os.path.curdir, "venv/lib/python3.7/site-packages"))  # 载入环境
from threading import Semaphore, Timer

from spyderpro.managerfunction.managerscence import ManagerScence
from spyderpro.managerfunction.managertraffic import ManagerTraffic

manage_scenece = ManagerScence()
manage_traffic = ManagerTraffic()
lock_scenece = Semaphore(1)
lock_change = Semaphore(1)
lock_traffic = Semaphore(1)


def monitoring_scencepeople_change():
    """
    监控地区人口变化

    """
    print("monitoring_scencepeople_change start")
    try:
        manage_scenece.manager_scenece_people()
    except Exception as e:
        print(e)
        pass
    lock_change.release()


def monitoring_scencepeople():
    print("monitoring_scencepeople start")

    try:
        manage_scenece.manager_scence_situation()
    except Exception as e:
        pass
    lock_scenece.release()


def monitoring_traffic():
    print("monitoring_traffic start")

    try:
        manage_traffic.manager_city_traffic()
    except Exception as e:
        pass
    lock_traffic.release()


if __name__ == "__main__":
    monitoring_scencepeople_change()
    monitoring_scencepeople()
    monitoring_traffic()
    while 1:
        # now = datetime.datetime.now()
        # #22：30---23：30不用运行，因为此时正在删除
        # if (now.hour == 23 and now.minute < 30) or (now.hour == 22 and now.minute > 30):
        #     time.sleep(3600)
        lock_scenece.acquire()
        # lock_change.acquire()
        lock_traffic.acquire()
        # Timer(interval=10, function=monitoring_scencepeople_change).start()
        Timer(interval=10, function=monitoring_scencepeople).start()
        Timer(interval=10, function=monitoring_traffic).start()


        # Timer(interval=300, function=monitoring_scencepeople_trend).start()
