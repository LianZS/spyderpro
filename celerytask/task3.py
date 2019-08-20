from .celeryconfig import app
from spyderpro.managerfunction.managerscence import ManagerScence

manage = ManagerScence()


@app.task(queue='location')
def monitoring_scencepeople():
    """
    监控景区人流
  
    """
    manage.manager_scence_situation()

    pass


@app.task(queue='location')
def monitoring_scencepeople_trend():
    """
    监控地区人口趋势
  
    """
    manage.manager_scence_trend()


@app.task(queue='location')
def monitoring_scencepeople_change():
    """
    监控地区人口变化
  
    """
    manage.manager_scenece_people()


@app.task(queue='location')
def people_positioning():
    """
    人口定位数据
   
    """
    pass


@app.task(queue='location')
def statistics_scencepeople():
    """
    统计昨天一整天的人流情况并且录入数据库¬

    """
    manage.manager_history_sceneceflow()


@app.task(queue='location')
def clear_scenceflow():
    """
    15天清除一遍scenceflow表
    """
    manage.clear_sceneflow_table()
@app.task(queue='location')
def clear_scence_distribution():
    """
    每天凌晨5点,晚23点清空人口分布密度数据表
    :return:
    """
    manage.clear_peopleposition_table()
# monitoring_scencepeople.delay()
# monitoring_scencepeople_trend.delay()
# monitoring_scencepeople_change.delay()
