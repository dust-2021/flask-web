from flask import Flask
from flask_session import Session
from configs import Config
from appFiles.bluePrint.consolePrints.web_console import web_console
from appFiles.bluePrint.index_page import index_page
from appFiles.bluePrint.consolePrints.sql_mapper import sql_mapper
from appFiles.bluePrint.consolePrints.test import tes
from appFiles.appTools.jobs import Aps


def create_app():
    app = Flask(__name__, template_folder='./templates', static_folder='./static')
    app.config.from_object(Config())
    app.register_blueprint(web_console, url_prefix='/web_console')
    app.register_blueprint(index_page, url_prefix='/')
    app.register_blueprint(sql_mapper, url_prefix='/sql_mapper')
    app.register_blueprint(tes, url_prefix='/test')
    # Bootstrap(app)
    # login session
    theSession = Session()
    theSession.init_app(app)
    # scheduler app
    aps = Aps()
    aps.init_app(app)
    aps.start(paused=True)
    return app, aps
