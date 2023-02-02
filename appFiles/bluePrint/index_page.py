from flask import Blueprint, jsonify
from flask import session, redirect, request, render_template
from appFiles.appTools.others import *
from appFiles.sql.databaseForWeb import web_db_session
from appFiles.appTools.smtp import Smtp
from sqlalchemy.sql import func

index_page = Blueprint('index_page', __name__)


@index_page.route('/')
def index():
    return render_template('index/index.html')
