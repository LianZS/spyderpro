import os
from .celeryconfig import app
from spyderpro.managerfunction.managerappinfo import ManagerApp

rootpath = os.path.dirname(os.path.abspath(os.path.pardir))
mapp = ManagerApp()


@app.task(queue='app')
def monitoring_app_userhabit():
    appinfo_filepath = os.path.join(rootpath, 'datafile/normalInfo/appinfo.csv')
    appbaseinfo_path = os.path.join(rootpath, 'datafile/normalInfo/appbaseinfo.csv')
    mapp.manager_app_userhabit(appinfo_filepath, appbaseinfo_path)


@app.task(queue='app')
def monitoring_user_behavior():
    filepath = os.path.join(rootpath, 'datafile/整体用户行为.csv')
    mapp.manager_user_behavior(filepath)


@app.task(queue='app')
def monitoring_app_active_data():
    mapp.manager_app_active_data()
# celery -A celerytask worker -l info
# celery worker -A celerytask -l info
# celery beat -A celerytask -l info
