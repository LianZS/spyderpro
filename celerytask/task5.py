from .celeryconfig import app


@app.task(queue='traffic')
def monitoring_weather_state():
    """
    监控天气状态

    """
    pass
