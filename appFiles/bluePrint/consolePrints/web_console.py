"""
console page blueprint
"""
from flask import Blueprint, jsonify
from flask import session, redirect, request, render_template
from appFiles.appTools.others import *
from appFiles.sql.databaseForWeb import web_db_session
from sqlalchemy.sql import func
from appFiles.sql.databaseForData import web_data_session
from flask import url_for

web_console = Blueprint('web_console', __name__)


@web_console.route('/')
@session_check
def index():
    """
    main page
    :return:
    """
    return render_template('console/base.html')


@web_console.route('/jobs')
@grant_checker(6)
@session_check
def jobs():
    """
    the page of scheduler jobs
    :return:
    """
    return render_template('console/jobs.html')


@web_console.route('/analysis')
@grant_checker(0)
def analysis():
    """
    the page for attr data analysis
    :return:
    """
    return render_template('console/analysis.html')


@web_console.route('/page_make')
@session_check
@grant_checker(4)
def page_make():
    """

    :return:
    """
    return render_template('console/page_make.html')


@web_console.route('/analysis/event')
@grant_checker(0)
def analysis_event():
    """
    :return the page of analysis event data
    :return:
    """
    return render_template('console/analysis_event.html')


@web_console.route('/columns_conf')
@grant_checker(4)
def columns_conf():
    """
    the page for configure columns
    :return:
    """
    return render_template('console/columns_conf.html')


@web_console.route('/permission_denied')
def permission_denied():
    """
    permission denied page
    :return:
    """
    return render_template('permission_denied.html')


@web_console.route('/login', methods=['GET', 'POST'])
def login():
    """
    web user login api, accept a multi-dict for username, password and remember.
    :return:
    """
    if request.method == 'GET':
        if session.get('username'):
            return redirect(url_for('web_console.index'))
        else:
            return render_template('console/login.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')

        result = web_db_session.query(UserTab.user_id, UserTab.passwordMD5).filter_by(
            username=username).first()
        if not result:
            # login failed return
            data = {'message': False}
            return jsonify(data)
        else:
            user_id, pw_md5 = result

        hash_worker = hashlib.md5()
        hash_worker.update(password.encode('utf-8'))
        md5_input = hash_worker.hexdigest()
        if pw_md5 and md5_input == pw_md5:
            if remember is not None and (remember == 'true' or remember == 'on'):
                session['username'] = username
                session['user_id'] = user_id
                session.permanent = datetime.timedelta(days=1)
            else:
                session['username'] = username
                session['user_id'] = user_id
                session.permanent = datetime.timedelta(minutes=30)
            data = {"message": True}
            # write login log
            now = datetime.datetime.now()
            # X-Real-IP the true ip when use nginx
            ip = request.headers.get('X-Real-IP', request.remote_addr)
            user_login = UserLogin(user_id=user_id, ip=ip,
                                   event_time=int(datetime.datetime.timestamp(now)), event_date=now)
            web_db_session.add(user_login)
            web_db_session.commit()
        else:
            session['username'] = username
            session.permanent = False
            data = {"message": False}
        web_db_session.close()
        return jsonify(data)
    else:
        return "unknown request method"


@web_console.route('/simple_login')
def simple_login():
    session['username'] = 'test_user'
    user_id = web_db_session.query(UserTab.user_id).filter_by(username='test_user').first()[0]
    session['user_id'] = user_id

    now = datetime.datetime.now()
    # X-Real-IP the true ip when use nginx
    ip = request.headers.get('X-Real-IP', request.remote_addr)
    user_login = UserLogin(user_id=user_id, ip=ip,
                           event_time=int(datetime.datetime.timestamp(now)), event_date=now)
    web_db_session.add(user_login)

    return redirect(url_for('web_console.index'))


@web_console.route('/test', methods=['GET', 'POST'])
def test():
    user_id = web_db_session.query(UserTab.user_id).filter_by(username=session.get('username')).first()[0]
    res = web_db_session.query(UserMsg.msg_title, UserMsg.msg_type, UserMsg.msg_text).filter_by(
        receiver_id=user_id, read_state=0).all()
    res = [{"msg_title": x[0], "msg_type": x[1], "msg_text": x[2]} for x in res]
    resp = {
        "msg_count": len(res),
        "msgs": res
    }
    web_db_session.close()
    return jsonify(resp)


@web_console.route('/current_user')
@session_check
def current_user():
    """
    current username
    :return: username
    """
    username = session.get('username')
    return username


@web_console.route('/logout')
@session_check
def logout():
    """
    logout, then clear the session
    :return: None
    """
    username = session.get('username')
    user_id = web_db_session.query(UserTab.user_id).filter_by(username=username).first()[0]
    now = datetime.datetime.now()
    ip = request.headers.get('X-Real-IP', request.remote_addr)
    # write logout log
    log = UserLogout(user_id=user_id, event_time=int(datetime.datetime.timestamp(now)), event_date=now, ip=ip)
    web_db_session.add(log)
    web_db_session.commit()
    web_db_session.close()
    session.clear()
    return 'success', 200


@web_console.route('/register')
def register():
    """
    the page route of register page
    :return:
    """
    max_id = web_db_session.query(func.max(UserTab.user_id)).first()[0]
    web_db_session.close()
    return render_template('console/register.html', default_userid='user' + str(max_id + 100001))


@web_console.route('/account/register', methods=['POST'])
def account_register():
    """
    register api, accept multi-dict info for register
    :return: register result
    """
    reData = {"message": None, "success": False}

    username = request.form.get('username')
    if len(username) > 64 or len(username) < 4:
        reData['message'] = '用户名长度必须在4至64个字符之间'
        return reData
    if web_db_session.query(UserTab.username).filter_by(username=username).first():
        web_db_session.close()
        reData['message'] = '用户名已存在'
        return reData
    password = request.form.get('password')

    hash_work = hashlib.md5()
    hash_work.update(password.encode('utf-8'))

    passwordMD5 = hash_work.hexdigest()
    new_user = UserTab(username=username, grant_level=1, passwordMD5=passwordMD5)

    web_db_session.add(new_user)
    web_db_session.commit()
    # write register log
    ip = request.headers.get('X-Real-IP', request.remote_addr)
    user_id = web_db_session.query(UserTab.user_id).filter_by(username=username).first()[0]
    now = datetime.datetime.now()
    log = UserRegister(username=username, user_id=user_id, ip=ip, event_time=int(datetime.datetime.timestamp(now)),
                       event_date=now)
    web_db_session.add(log)
    web_db_session.commit()
    web_db_session.close()
    reData['success'] = True
    return reData


@web_console.route('/account/delete/<user_id>')
@session_check
@grant_checker(10)
def account_del(user_id):
    user = UserTab(user_id=user_id)
    if web_db_session.query(UserTab.username).filter_by(user_id=user_id).first()[0] == 'root':
        return 'root账号不可删除', 200
    web_db_session.delete(user)
    web_db_session.commit()
    web_db_session.close()
    return 'success', 200


@web_console.route('/message/state')
@session_check
def user_message_state():
    """
    get the message which haven't been reading.
    :return:
    """
    user_id = session.get('user_id')
    resp = web_db_session.query(UserMsg.msg_title).filter_by(receiver_id=user_id, read_state=0).all()
    web_db_session.close()
    data = {"counts": 0, 'titles': []}
    if len(resp) == 0:
        return jsonify(data)
    else:
        data['counts'] = len(resp)
        data['titles'] = [x[0] for x in resp]
        return jsonify(data)


@web_console.route('/message/read_all')
@session_check
def user_message_read_all():
    """
    turn all msg's read state to 1
    :return:
    """
    user_id = session.get('user_id')
    web_db_session.query(UserMsg).filter_by(receiver_id=user_id).update({UserMsg.read_state: 1})
    web_db_session.commit()
    web_db_session.close()
    return 'success', 200
