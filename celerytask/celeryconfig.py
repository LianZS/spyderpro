import sys
import os

# sys.path[0] = os.path.abspath(os.path.join(os.path.pardir,
#                                            "/Users/darkmoon/Project/SpyderPr/venv/lib/python3.7/site-packages/"))  # 载入环境from celery.schedules import crontab
# sys.path[0] = os.path.abspath("./venv/lib/python3.7/site-packages/")
sys.path[0] ="/home/spyder/lib/python3.7/site-packages/"

from celery.schedules import crontab
from celery import Celery
from kombu import Queue, Exchange

app = Celery()
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_IMPORTS = (
    'celerytask.appinfo_task', 'celerytask.keyword_task', 'celerytask.scence_task', 'celerytask.traffic_task',
    'celerytask.weather_task', 'celerytask.raw_task','celerytask.clear_logs',)  # 导入指定任务墨模块

CELERYBEAT_SCHEDULE = {
    'dailycitytraffic': {
        'task': 'celerytask.traffic_task.monitoring_dailycitytraffic',
        'schedule': crontab('*/30'),  # 30分钟执行一遍
    },
    'roadtraffic': {
        'task': 'celerytask.traffic_task.monitoring_roadtraffic',
        'schedule': crontab('*/30'),  # 30分钟执行一遍
    },
    'yeartraffic': {
        'task': 'celerytask.traffic_task.monitoring_yeartraffic',
        'schedule': crontab(minute=0, hour=7),  # 每天早上7点运行一次
    },

    'scence_situation': {
        'task': 'celerytask.scence_task.monitoring_scencepeople',
        'schedule': crontab('*/30'),  # 每天30min运行一次
    },
    'scencepeople_trend': {
        'task': 'celerytask.scence_task.monitoring_scencepeople_trend',
        'schedule': crontab('*/5'),  # 每天5min运行一次
    },
    'scencepeople_change': {
        'task': 'celerytask.scence_task.monitoring_scencepeople_change',
        'schedule': crontab('*/5'),  # 每5min运行一次
    },
    'scencepeople_history': {
        'task': 'celerytask.scence_task.statistics_scencepeople',
        'schedule': crontab(minute=3, hour=1),  # 每天凌晨01：03运行
    },

    'keyword_rate': {
        'task': 'celerytask.keyword_task.monitoring_keyword_rate',
        'schedule': crontab(minute=0, hour=12),  # 每天12点运行一次
    },
    'app_active': {
        'task': 'celerytask.appinfo_task.monitoring_app_active_data',
        'schedule': crontab(0, 0, day_of_month='15'),  # 每个月的第15天执行。
    },
    'weather_air_state': {
        'task': 'celerytask.weather_task.monitoring_weather_state',
        'schedule': crontab('*/60'),  # 空气监测。
    },
    "raw_air_state": {
        "task": "celerytask.raw_task.monitoring_airstatus_raw",
        'schedule': crontab(minute=0, hour='*/3')	,  # 缓存数据空气质量检测

    },
    "raw_scence_state": {
        "task": "celerytask.raw_task.monitoring_scence_raw",
        'schedule': crontab(minute=7, hour='*/2')	,  # 缓存数据景区流量检测

    },
    "raw_traffic_state": {
        "task": "celerytask.raw_task.monitoring_traffic_raw",
        'schedule': crontab(minute=0, hour='*/2')	,  # 缓存数据交通检测

    },
    "clear": {
        "task": "celerytask.clear_logs.clear_mysql_log_bin",
        'schedule': crontab(minute=0, hour='*/3')	,

    },

}  # 默认的定时调度程序
CELERY_QUEUES = (
    Queue('default', exchange=Exchange('default', type='direct', delivery_mode=1, durable=False)),
    Queue('app', routing_key='celerytask.appinfo_task.#', exchange=Exchange('appinfo_task', type='direct')),
    Queue('Internet', routing_key='celerytask.keyword_task.#', exchange=Exchange('keyword_task', type='direct')),
    Queue('scence_people_change', routing_key='celerytask.scence_task.monitoring_scencepeople_change',
          exchange=Exchange('scence_task', type='direct')),
    Queue('scence_trend', routing_key='celerytask.scence_task.monitoring_scencepeople_trend',
          exchange=Exchange('scence_task', type='direct')),
    Queue('baidu_scence_people', routing_key='celerytask.scence_task.monitoring_scencepeople',
          exchange=Exchange('scence_task', type='direct')),

    Queue('daily_traffic', routing_key='celerytask.traffic_task.monitoring_dailycitytraffic',
          exchange=Exchange('traffic_task', type='direct')),

    Queue('road_traffic', routing_key='celerytask.traffic_task.monitoring_roadtraffic',
          exchange=Exchange('traffic_task', type='direct')),
    Queue('year_traffic', routing_key='celerytask.traffic_task.monitoring_yeartraffic',
          exchange=Exchange('traffic_task', type='direct')),

    Queue('weather', routing_key='celerytask.weather_task.#', exchange=Exchange('weather_task', type='direct')),
    Queue('raw_status', routing_key='celerytask.raw_task.#', exchange=Exchange('raw_status', type='direct')),

)  # 自定义队列
CELERY_TASK_DEFAULT_QUEUE = 'default'  # 默认队列
CELERY_ROUTES = {
    'celerytask.appinfo_task.*': {'queue': 'app'},
    'celerytask.keyword_task.*': {'queue': 'Internet'},
    'celerytask.scence_task.monitoring_scencepeople_change': {'queue': 'scenece_people_change'},
    'celerytask.scence_task.monitoring_scencepeople_trend': {'queue': 'scence_trend'},
    'celerytask.scence_task.monitoring_scencepeople': {'queue': 'baidu_scence_people'},

    # 'celerytask.scence_task.*': {'queue': 'location'},
    'celerytask.traffic_task.monitoring_dailycitytraffic': {'queue': 'daily_traffic'},

    'celerytask.traffic_task.monitoring_roadtraffic': {'queue': 'road_traffic'},

    'celerytask.traffic_task.monitoring_yeartraffic': {'queue': 'year_traffic'},

    'celerytask.weather_task.*': {'queue': 'weather'},
    'celerytask.raw_task.*': {'queue': 'raw_status'},

}  # 路由器列表
CELERYD_CONCURRENCY = 30  # 设置并发的worker数量

CELERYD_MAX_TASKS_PER_CHILD = 100  # 每个worker最多执行100个任务被销毁，可以防止内存泄漏
CELERY_TASK_ACKS_LATE = True  # 允许重试
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True
CELERY_REDIS_BACKEND_USE_SSL = {

}  # Redis后端支持SSL
