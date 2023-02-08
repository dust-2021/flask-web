import pickle

from flask import Blueprint, jsonify
from flask import session, redirect, request, render_template
from appFiles.appTools.others import *
from appFiles.sql.databaseForWeb import web_db_session
from sqlalchemy.sql import func
from appFiles.sql.databaseForData import web_data_session
from flask import url_for

app_api = Blueprint('api', __name__)


@app_api.route('/mapper_reload/<int:mapper_id>')
@session_check
def reload_mapper(mapper_id):
    class_text = web_db_session.query(UserMapper.mapper_pickle).filter_by(mapper_id=mapper_id).first()
    resp = {'status': None, 'message': None, 'data': None}
    if class_text:
        mapper_obj = pickle.loads(class_text[0])
        resp['status'] = 'SUCCESS'
        resp['data'] = mapper_obj.query



