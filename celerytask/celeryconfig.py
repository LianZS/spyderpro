import sys
import os

sys.path[0] = os.path.abspath(os.path.join(os.path.curdir, "venv/lib/python3.7/site-packages"))
from celery.schedules import crontab
from celery import Celery
from kombu import Queue, Exchange

app = Celery()
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_IMPORTS = (
    'celerytask.task1', 'celerytask.task2', 'celerytask.task3', 'celerytask.task4', 'celerytask.task5')  # 导入指定任务墨模块

CELERYBEAT_SCHEDULE = {
    'dailycitytraffic': {
        'task': 'celerytask.task4.monitoring_dailycitytraffic',
        'schedule': crontab('*/5'),  # 5分钟执行一遍
    },
    'roadtraffic': {
        'task': 'celerytask.task4.monitoring_roadtraffic',
        'schedule': crontab('*/10'),  # 12分钟执行一遍
    },
    'yeartraffic': {
        'task': 'celerytask.task4.monitoring_yeartraffic',
        'schedule': crontab(minute=0, hour=7),  # 每天早上7点运行一次
    },
    'scence_situation': {
        'task': 'celerytask.task3.monitoring_scencepeople',
        'schedule': crontab('*/30'),  # 每天30min运行一次
    },
    'scencepeople_trend': {
        'task': 'celerytask.task3.monitoring_scencepeople_trend',
        'schedule': crontab('*/13'),  # 每天13min运行一次
    },
    'scencepeople_change': {
        'task': 'celerytask.task3.monitoring_scencepeople_change',
        'schedule': crontab('*/12'),  # 每天12min运行一次
    },
    'keyword_rate': {
        'task': 'celerytask.task2.monitoring_keyword_rate',
        'schedule': crontab(minute=0, hour=12),  # 每天12点运行一次
    },
    'app_active': {
        'task': 'celerytask.task1.monitoring_app_active_data',
        'schedule': crontab(0, 0, day_of_month='15'),  # 每个月的第15天执行。
    },

}  # 默认的定时调度程   序
CELERY_QUEUES = (
    Queue('default', exchange=Exchange('default', type='direct', delivery_mode=1, durable=False)),
    Queue('app', routing_key='celerytask.task1.#', exchange=Exchange('task1', type='direct')),
    Queue('Internet', routing_key='celerytask.task2.#', exchange=Exchange('task2', type='direct')),
    Queue('location', routing_key='celerytask.task3.#', exchange=Exchange('task3', type='direct')),
    Queue('traffic', routing_key='celerytask.task4.#', exchange=Exchange('task4', type='direct')),
    Queue('weather', routing_key='celerytask.task5.#', exchange=Exchange('task5', type='direct')),

)  # 自定义队列
CELERY_TASK_DEFAULT_QUEUE = 'default'  # 默认队列
CELERY_ROUTES = {
    'celerytask.task1.*': {'queue': 'app'},
    'celerytask.task2.*': {'queue': 'Internet'},
    'celerytask.task3.*': {'queue': 'location'},
    'celerytask.task4.*': {'queue': 'traffic'},
    'celerytask.task5.*': {'queue': 'weather'},

}  # 路由器列表
CELERYD_CONCURRENCY = 4  # 设置并发的worker数量

CELERYD_MAX_TASKS_PER_CHILD = 100  # 每个worker最多执行100个任务被销毁，可以防止内存泄漏
CELERY_TASK_ACKS_LATE = True  # 允许重试
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True
CELERY_REDIS_BACKEND_USE_SSL = {

}  # Redis后端支持SSL
