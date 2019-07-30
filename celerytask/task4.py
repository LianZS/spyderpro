from spyderpro.managerfunction.managertraffic import ManagerTraffic

from .celeryconfig import app

traffic = ManagerTraffic()


@app.task(queue='traffic')
def monitoring_dailycitytraffic():
    """
        监控城市实时交通拥堵情况
    """
    traffic.manager_city_traffic()


@app.task(queue='traffic')
def monitoring_roadtraffic():
    """
        监控城市道路实时交通拥堵情况
    """
    traffic.manager_city_road_traffic()


@app.task(queue='traffic')
def monitoring_yeartraffic():
    """
        监控城市日交通拥堵情况
    """
    traffic.manager_city_year_traffic()


@app.task(queue='traffic')
def clear_roadtraffic():
    traffic.clear_road_data()
# monitoring_roadtraffic.delay()
# monitoring_dailycitytraffic.delay()
# monitoring_roadtraffic.delay()
