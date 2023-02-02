"""
api for web test
"""
from flask import Blueprint
from appFiles.celeryProj.celery_task.celery_manage import celery
from celery.result import AsyncResult
from appFiles.celeryProj.celery_task.tasks import celery_test
from flask import jsonify

tes = Blueprint('test', __name__)


@tes.route('/test_func_celery')
def test_func_celery():
    task_id = celery_test.delay().id
    return task_id


@tes.route('/task_status/<task_id>')
def test_func_celery_task_status(task_id):
    res = AsyncResult(task_id, app=celery).status
    return res


@tes.route('/task_result/<task_id>')
def test_func_celery_task_result(task_id):
    res = AsyncResult(task_id, app=celery).result
    return res
