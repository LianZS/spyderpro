from celery import Celery
import ssl

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_IMPORTS = ()  # 导入指定任务墨模块

CELERYBEAT_SCHEDULE = {

}  # 默认的定时调度程序
CELERY_QUEUES = ()  # 自定义队列
CELERY_TASK_DEFAULT_QUEUE = ''  # 默认队列
CELERY_ROUTES = {

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
