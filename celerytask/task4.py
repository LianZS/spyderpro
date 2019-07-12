from .loads import *


@app.task( queue='traffic')
def monitoring_dailycitytraffic():
    """
        监控城市实时交通拥堵情况
    """
    pass


@app.task( queue='traffic')
def monitoring_roadtraffic():
    """
        监控城市道路实时交通拥堵情况
    """
    pass


@app.task( queue='traffic')
def monitoring_roadtraffic():
    """
        监控城市道路实时交通拥堵情况
    """
    pass


@app.task( queue='traffic')
def monitoring_yeartraffic():
    """
        监控城市日交通拥堵情况
    """
    pass
