from flask import Blueprint, jsonify
from flask import session, redirect, request, render_template
from appFiles.appTools.others import *
from appFiles.sql.databaseForWeb import web_db_session
from sqlalchemy.sql import func
from appFiles.sql.databaseForData import web_data_session
from flask import url_for

web_backend = Blueprint('web_backend', __name__)


@web_backend.route('/backend/person')
@session_check
def person_backend():
    ...

