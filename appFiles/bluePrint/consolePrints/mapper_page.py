from flask import session, jsonify, request, Blueprint
from appFiles.appTools.others import session_check, grant_checker
from appFiles.sql.databaseForWeb import *
from appFiles.sql.databaseForData import *
from appFiles.sql.mapper_generator import EchartsGenerator
from appFiles.sql.mapper_generator import SqlMapper
from appFiles.celeryProj.celery_task.celery_manage import celery
from appFiles.celeryProj.celery_task.tasks import celery_mapper_executor, celery_test
from celery.result import AsyncResult
from configs import DataConfig
from hashlib import md5

mapper_page = Blueprint('mapper_page', __name__)


@mapper_page.route('/page/create', methods=['POST'])
@session_check
def create_page():
    req = request.form

