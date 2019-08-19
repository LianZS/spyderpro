import sys
import os
import time
# sys.path[1] =os.path.abspath(os.path.join(os.path.curdir))
sys.path[0] = os.path.abspath(os.path.join(os.path.curdir, "venv/lib/python3.7/site-packages"))  # 载入环境
from threading import Semaphore, Timer

from spyderpro.managerfunction.managerscence import ManagerScence

manage = ManagerScence()
lock_trend = Semaphore(1)
lock_change = Semaphore(1)


def monitoring_scencepeople_trend():
    """
    监控地区人口趋势

    """
    try:
        manage.manager_scence_trend()
    except Exception:
        return
    lock_trend.release()


def monitoring_scencepeople_change():
    """
    监控地区人口变化

    """

    try:
        manage.manager_scenece_people()
    except Exception:
        return
    lock_change.release()



if __name__ == "__main__":
    while 1:
        lock_trend.acquire()
        lock_change.acquire()
        Timer(interval=10, function=monitoring_scencepeople_change).start()

        Timer(interval=300, function=monitoring_scencepeople_trend).start()
