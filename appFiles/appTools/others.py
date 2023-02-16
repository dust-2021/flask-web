from functools import wraps
from flask import session, redirect, url_for
from appFiles.sql.databaseForWeb import *


def session_check(func):
    """
    check the request sender's session, if the request without session,then redirect
    sender to the login page.
    :param func: the route function
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('username'):
            # reset the ttl of session
            session.modified = True
            return func(*args, **kwargs)
        else:
            return redirect(url_for('web_console.login'))

    return wrapper


def grant_checker(grant_level):
    def grant_check(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            username = session.get('username')
            user_grant_level = web_db_session.query(UserTab.grant_level).filter_by(username=username).first()
            if user_grant_level[0] >= grant_level:
                result = func(*args, **kwargs)
                return result
            else:
                return redirect(url_for('web_console.permission_denied'))

        return wrapper

    return grant_check


class CustomJsonEncoder(json.JSONEncoder):
    def __init__(self, args, kwargs):
        super().__init__(*args, **kwargs)

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.__repr__()
