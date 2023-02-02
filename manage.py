from appFiles.app import create_app
from appFiles.appTools.jobs import job_checker
from randomData import random_insert

app, aps = create_app()
aps.add_job(id='job_checker', func=job_checker, trigger='cron', minute='*/1', second='0', replace_existing=True)
aps.add_job(id='random_data', func=random_insert, trigger='cron', day='*', hour='*/4', replace_existing=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
