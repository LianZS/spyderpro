from .celeryconfig import *

from spyderpro.managerfunction.managertraffic import ManagerTraffic


@app.task(queue='financial')
def add():
    pass



# celery -A celerytask worker -l info
