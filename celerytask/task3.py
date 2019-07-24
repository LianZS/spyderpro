from .celeryconfig import app
from spyderpro.managerfunction.managerscence import ManagerScence


@app.task(queue='location')
def monitoring_scencepeople():
    """
    监控景区人流
  
    """
    ManagerScence().manager_scence_situation()

    pass


@app.task(queue='location')
def monitoring_scencepeople_trend():
    """
    监控地区人口趋势
  
    """
    ManagerScence().manager_scence_trend()
    pass


@app.task(queue='location')
def monitoring_scencepeople_change():
    """
    监控地区人口变化
  
    """
    ManagerScence().manager_scenece_people()
    pass


@app.task(queue='location')
def people_positioning():
    """
    人口定位数据
   
    """
    pass
