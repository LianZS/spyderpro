from .celeryconfig import app
import os
from spyderpro.manager_function.manager_keyword import ManagerMobileKey

rootpath = os.path.dirname(os.path.abspath(os.path.pardir))


@app.task(queue='Internet')
def monitoring_keyword_rate():
    """
    获取浏览器景区关键词搜索频率

    """
    ManagerMobileKey().manager_search()


@app.task(queue='Internet')
def monitoring_mobile_type_rate():
    """
    获取某个时段的中国境内各手机机型的占有率"""
    m = ManagerMobileKey()
    filepath = os.path.join(rootpath, 'datafile/苹果手机品牌占有率.csv')
    mobiletype = 1
    m.manager_mobile_type_rate(mobiletype, filepath)
    filepath = os.path.join(rootpath, 'datafile/安卓手机品牌占有率.csv')
    mobiletype = 2
    m.manager_mobile_type_rate(mobiletype, filepath)


@app.task(queue='Internet')
def monitoring_mobile_brand_rate():
    """
    获取某时段中国境内各手机品牌占用率

    """
    filepath = os.path.join(rootpath, 'datafile/品牌占有率.csv')

    ManagerMobileKey().manager_mobile_brand_rate(filepath)


@app.task(queue='Internet')
def monitoring_mobile_system_rate():
    """
    获取某时段中国境内各手机系统版本占用率
    """
    filepath = os.path.join(rootpath, 'datafile/苹果系统占有率.csv')
    mobiletype = 1
    ManagerMobileKey().manager_mobile_system_rate(mobiletype, filepath)
    filepath = os.path.join(rootpath, 'datafile/安卓系统占有率.csv')
    mobiletype = 2
    ManagerMobileKey().manager_mobile_system_rate(mobiletype, filepath)


@app.task(queue='Internet')
def monitoring_mobile_operator_rate():
    """获取某时段中国境内各手机运营商占用率"""
    filepath = os.path.join(rootpath, 'datafile/运营商占有率.csv')

    ManagerMobileKey().manager_mobile_operator_rate(filepath)


@app.task(queue='Internet')
def monitoring_mobile_network_rate():
    """获取某时段中国境内各手机网络占用率"""
    filepath = os.path.join(rootpath, 'datafile/网络占有率.csv')

    ManagerMobileKey().manager_mobile_network_rate(filepath)


