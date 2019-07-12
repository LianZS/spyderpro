from .loads import *


@app.task(bind=True, queue='location')
def monitoring_scencepeople():
    """
    监控景区人流
  
    """

    pass


@app.task(bind=True, queue='location')
def monitoring_scencepeople_trend():
    """
    监控地区人口趋势
  
    """
    pass


@app.task(bind=True, queue='location')
def monitoring_scencepeople_change():
    """
    监控地区人口变化
  
    """
    pass


@app.task(bind=True, queue='location')
def people_positioning():
    """
    人口定位数据
   
    """
    pass

