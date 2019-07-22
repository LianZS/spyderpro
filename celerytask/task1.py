from .celeryconfig import *

from spyderpro.managerfunction.managertraffic import ManagerTraffic


@app.task(queue='financial')
def add():
    pass



# celery -A celerytask worker -l info
# celery worker -A celerytask -l info
# celery beat -A celerytask -l info