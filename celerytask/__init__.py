from celery import Celery

from celerytask import celeryconfig

app = Celery()
app.config_from_object(celeryconfig)
