import pickle

from flask import Blueprint, jsonify
from flask import session, redirect, request, render_template
from appFiles.appTools.others import *
from appFiles.sql.databaseForWeb import web_db_session
from sqlalchemy.sql import func
from appFiles.sql.databaseForData import web_data_session
from flask import url_for
from sqlalchemy.sql import func
from sqlalchemy import or_, and_

mapper_page_api = Blueprint('mapper_page_api', __name__)


@mapper_page_api.route('/mapper/reload/<int:mapper_id>')
@session_check
def reload_mapper(mapper_id):
    class_text = web_db_session.query(UserMapper.mapper_pickle).filter_by(mapper_id=mapper_id).first()
    resp = {'status': None, 'message': None, 'data': None}
    web_db_session.close()
    if class_text:
        mapper_obj = pickle.loads(class_text[0])
        resp['status'] = 'SUCCESS'
        resp['data'] = mapper_obj.query


@mapper_page_api.route('/mapper/select/<int:mapper_id>')
@session_check
def select_stored_mapper(mapper_id):
    resp = {
        'status': None,
        'message': None,
        'data': None
    }

    try:
        mapper_id = int(mapper_id)
    except Exception as ex:
        print(ex)
        resp['message'] = '错误编号'
        return jsonify(resp)
    if mapper_id == 0:
        res = web_db_session.query(UserMapper.mapper_id, UserMapper.mapper_name).filter(
            or_(UserMapper.user_id == session.get('user_id'), UserMapper.mark_level == 3)).all()
        web_db_session.close()
        resp['data'] = [list(x) for x in res]
        resp['status'] = 'SUCCESS'
        return jsonify(resp)
    else:
        res = web_db_session.query(UserMapper.mapper_id, UserMapper.mapper_name).filter_by(mapper_id=mapper_id).first()
        web_db_session.close()
        if res:
            resp['data'] = list(res)
            resp['status'] = 'SUCCESS'
            return jsonify(resp)
        else:
            resp['message'] = 'mapper id error'
            resp['status'] = 'FAILED'
            return jsonify(resp)
