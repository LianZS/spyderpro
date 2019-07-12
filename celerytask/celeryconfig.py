import ssl
from kombu import Queue, Exchange
from celerytask import task1, task2, task3, task4, task5

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_IMPORTS = (task1, task2, task3, task4, task5)  # 导入指定任务墨模块

CELERYBEAT_SCHEDULE = {

}  # 默认的定时调度程序
CELERY_QUEUES = (
    Queue('default', exchange=Exchange('default', type='direct')),
    Queue('financial', routing_key='celerytask.task1.#', exchange=Exchange('task1', type='direct')),
    Queue('Internet', routing_key='celerytask.task2.#', exchange=Exchange('task2', type='direct')),
    Queue('location', routing_key='celerytask.task3.#', exchange=Exchange('task3', type='direct')),
    Queue('traffic', routing_key='celerytask.task4.#', exchange=Exchange('task4', type='direct')),
    Queue('weather', routing_key='celerytask.task5.#', exchange=Exchange('task5', type='direct')),

)  # 自定义队列
CELERY_TASK_DEFAULT_QUEUE = 'default'  # 默认队列
CELERY_ROUTES = {
    'celerytask.task1.*': 'financial',
    'celerytask.task2.*': 'Internet',
    'celerytask.task3.*': 'location',
    'celerytask.task4.*': 'traffic',
    'celerytask.task5.*': 'weather',

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
