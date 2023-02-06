from flask import Blueprint, jsonify
from flask import session, redirect, request, render_template
from appFiles.appTools.others import *
from appFiles.sql.databaseForWeb import web_db_session
from sqlalchemy.sql import func
from appFiles.sql.databaseForData import web_data_session
from flask import url_for
import hashlib

web_backend = Blueprint('web_backend', __name__)


@web_backend.route('/backend/person')
@session_check
def person_backend():
    ...


@web_backend.route('/backend/password_modify', methods=['POST'])
@session_check
def password_modify():
    req = request.form
    user_id = session.get('user_id')
    old_password = req.get('old_password')
    new_password = req.get('new_password')

    _hasher = hashlib.md5()
    _hasher.update(old_password.encode('utf-8'))
    old_pwd_md5 = _hasher.hexdigest()

    current_password = web_db_session.query(UserTab.passwordMD5).filter_by(id=user_id).first()

    resp = {'status': None, 'message': None}
    if current_password != old_pwd_md5:
        resp['status'] = 'FAILED'
        resp['message'] = '旧密码错误'
        return jsonify(resp)
    if old_password == new_password:
        resp['status'] = 'FAILED'
        resp['message'] = '新密码与旧密码相同'
        return jsonify(resp)

    _hasher = hashlib.md5()
    _hasher.update(new_password.encode('utf-8'))
    new_pwd_md5 = _hasher.hexdigest()
    web_db_session.query(UserTab.passwordMD5).filter_by(id=user_id).update({UserTab.passwordMD5: new_pwd_md5})
    web_db_session.commit()
    web_db_session.close()
    resp['status'] = 'SUCCESS'
    resp['message'] = ''
    return jsonify(resp)

