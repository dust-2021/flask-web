import datetime

import flask
import werkzeug

from appFiles.appTools.others import grant_checker, session_check
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
#
from appFiles.sql.databaseForWeb import engine
from flask_apscheduler import APScheduler, api
import logging

LOGGER = logging.getLogger('flask_apscheduler')

jobstores = {
    'default': SQLAlchemyJobStore(engine=engine)
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}


class NewApi:
    """
    重定义scheduler访问api， 增加权限机制
    """

    def __init__(self):
        pass

    @staticmethod
    @session_check
    @grant_checker(6)
    def add_job():
        return api.add_job()

    @staticmethod
    @session_check
    @grant_checker(10)
    def get_scheduler_info():
        return api.get_scheduler_info()

    @staticmethod
    @session_check
    @grant_checker(6)
    def get_job(job_id):
        return api.get_job(job_id=job_id)

    @staticmethod
    @session_check
    @grant_checker(6)
    def get_jobs():
        return api.get_jobs()

    @staticmethod
    @session_check
    @grant_checker(6)
    def delete_job(job_id):
        return api.delete_job(job_id=job_id)

    @staticmethod
    @session_check
    @grant_checker(6)
    def update_job(job_id):
        return api.update_job(job_id=job_id)

    @staticmethod
    @session_check
    @grant_checker(6)
    def pause_job(job_id):
        return api.pause_job(job_id=job_id)

    @staticmethod
    @session_check
    @grant_checker(6)
    def resume_job(job_id):
        return api.resume_job(job_id=job_id)

    @staticmethod
    @session_check
    @grant_checker(6)
    def run_job(job_id):
        return api.run_job(job_id=job_id)


class Aps(APScheduler):
    """
    再封装定时任务调度器，在api接口添加权限设置，修改api加载顺序，api将在aps调用
    start()方法添加
    """

    def __init__(self):
        super().__init__()

    def init_app(self, app):
        """Initialize the APScheduler with a Flask application instance."""

        self.app = app
        self.app.config.update({'SCHEDULER_JOBSTORES': jobstores,
                                'SCHEDULER_EXECUTORS': executors,
                                'SCHEDULER_JOB_DEFAULTS': job_defaults})
        self.app.apscheduler = self

        self._load_config()
        self._load_jobs()

    def start(self, paused=False):
        """
        Start the scheduler.
        :param bool paused: if True, don't start job processing until resume is called.
        """
        if self.api_enabled:
            self._load_api()

        # Flask in debug mode spawns a child process so that it can restart the process each time your code changes,
        # the new child process initializes and starts a new APScheduler causing the jobs to run twice.
        if flask.helpers.get_debug_flag() and not werkzeug.serving.is_running_from_reloader():
            return

        if self.host_name not in self.allowed_hosts and '*' not in self.allowed_hosts:
            LOGGER.debug('Host name %s is not allowed to start the APScheduler. Servers allowed: %s' %
                         (self.host_name, ','.join(self.allowed_hosts)))
            return

        self._scheduler.start(paused=paused)

    def _load_api(self):
        """
        Add the routes for the scheduler API.
        """
        self._add_url_route('get_scheduler_info', '', NewApi.get_scheduler_info, 'GET')
        self._add_url_route('add_job', '/jobs', NewApi.add_job, 'POST')
        self._add_url_route('get_job', '/jobs/<job_id>', NewApi.get_job, 'GET')
        self._add_url_route('get_jobs', '/jobs', NewApi.get_jobs, 'GET')
        self._add_url_route('delete_job', '/jobs/<job_id>', NewApi.delete_job, 'DELETE')
        self._add_url_route('update_job', '/jobs/<job_id>', NewApi.update_job, 'PATCH')
        self._add_url_route('pause_job', '/jobs/<job_id>/pause', NewApi.pause_job, 'GET')
        self._add_url_route('resume_job', '/jobs/<job_id>/resume', NewApi.resume_job, 'GET')
        self._add_url_route('run_job', '/jobs/<job_id>/run', NewApi.run_job, 'POST')


def job_checker():
    print(datetime.datetime.now())
