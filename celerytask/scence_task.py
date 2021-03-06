from .celeryconfig import app
from spyderpro.manager_function.manager_scence import ManagerScence


@app.task(queue='baidu_scence_people')
def monitoring_scencepeople():
    """
    监控景区人流
  
    """
    manage = ManagerScence()

    manage.manager_scence_situation()

    pass


@app.task(queue='scence_trend')
def monitoring_scencepeople_trend():
    """
    监控地区人口趋势
  
    """
    manage = ManagerScence()

    manage.manager_scence_trend()


@app.task(queue='scence_people_change')
def monitoring_scencepeople_change():
    """
    监控地区人口变化
  
    """
    manage = ManagerScence()

    manage.manager_scenece_people()

# @app.task(queue='location')
# def people_positioning():
#     """
#     人口定位数据
#
#     """
#     pass
