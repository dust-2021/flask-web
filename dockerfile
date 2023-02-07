FROM python:3.8
WORKDIR /dockerProject/dataAnalysis
#USER flask_user
COPY . .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
CMD gunicorn manage:app -c appFiles/configTemp/appLoadConfig/gunicorn.conf.py &&
celery -A appFiles.celeryProj.celery_task.celery_manage:celery worker -P eventlet \
      -l info