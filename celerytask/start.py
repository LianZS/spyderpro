import sys
import os
os.curdir=os.path.pardir
sys.path[0]="/Users/darkmoon/Project/SpyderPr/"
# sys.path[0] = os.path.abspath(os.path.join(os.path.curdir, "venv/lib/python3.7/site-packages"))  # 载入环境
os.system("celery -A celerytask worker -l info")
print(sys.path)