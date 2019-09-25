from spyderpro.manager_function.manager_traffic import ManagerTraffic

from .celeryconfig import app

traffic = ManagerTraffic()


@app.task(queue='daily_traffic')
def monitoring_dailycitytraffic():
    """
        监控城市实时交通拥堵情况
    """
    traffic.manager_city_traffic()


@app.task(queue='road_traffic')
def monitoring_roadtraffic():
    """
        监控城市道路实时交通拥堵情况
    """
    traffic.manager_city_road_traffic()


@app.task(queue='year_traffic')
def monitoring_yeartraffic():
    """
        监控城市日交通拥堵情况
    """
    traffic.manager_city_year_traffic()


