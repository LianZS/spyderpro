from .celeryconfig import app
import os
from spyderpro.manager_function.manager_raw import ManagerRAW

rootpath = os.path.dirname(os.path.abspath(os.path.pardir))


@app.task(queue='raw_status')
def monitoring_scence_raw():
    """
     检查景区数据缓存是否存在问题

    """
    ManagerRAW().manager_scence_data_raw()
    print("检查景区数据缓存是否存在问题")


@app.task(queue='raw_status')
def monitoring_traffic_raw():
    """
    检查交通数据缓存是否存在问题
    :return:
    """
    ManagerRAW().manager_citytraffic_data_raw()
    print("检查交通数据缓存是否存在问题")


@app.task(queue='raw_status')
def monitoring_airstatus_raw():
    """
    检查空气数据缓存是否存在问题
    :return:
    """
    ManagerRAW().manager_airstatus_data_raw()
    print("检查空气数据缓存是否存在问题")
