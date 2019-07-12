from .loads import *


@app.task(bind=True, queue='traffic')
def monitoring_weather_state():
    """
    监控天气状态

    """
    pass
