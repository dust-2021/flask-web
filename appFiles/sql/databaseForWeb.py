import datetime
import json
from sqlalchemy import Column, String, create_engine, Integer, Float, VARCHAR, Text, DateTime, BigInteger, Date, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os
import hashlib
from configs import Config, account_config


def engine_generator():
    account_configs = {}
    if Config.SQLALCHEMY_MEM == 'local':
        account_configs = account_config.get('mysql_local_conf')
    if Config.SQLALCHEMY_MEM == 'remote':
        account_configs = account_config.get('mysql_conf')
    _conf = Config.All_ARGS
    sql_url = "mysql+%s://%s:%s@%s/%s"
    sql_user = account_configs.get('username')
    sql_password = account_configs.get('password')
    sql_host = account_configs.get('host')
    sql_database = 'flask_web'
    sql_connector = 'pymysql'
    sql_pool_size = _conf['sqlalchemy_pool_size']
    sql_pool_recycle = _conf['sqlalchemy_pool_recycle']
    _engine = create_engine(sql_url % (sql_connector, sql_user, sql_password, sql_host, sql_database), pool_size=sql_pool_size,
                            pool_recycle=sql_pool_recycle)
    return _engine


Base = declarative_base()
engine = engine_generator()


class ApschedulerJobs(Base):
    __tablename__ = 'apscheduler_jobs'

    id = Column(VARCHAR(191), primary_key=True)
    next_run_time = Column(BigInteger)
    job_state = Column(BLOB)


class UserTab(Base):
    """
    user account for this web, create 'root' user at first if not exist
    """
    __tablename__ = 'User'

    username = Column(VARCHAR(64), unique=True)
    grant_level = Column(Integer)
    passwordMD5 = Column(VARCHAR(64))
    extendColumn = Column(String(64), default=None)
    user_id = Column(BigInteger, primary_key=True, autoincrement=True)


class UserRegister(Base):
    """
    user register log
    """
    __tablename__ = 'UserRegister'

    username = Column(String(64))
    user_id = Column(BigInteger, default=None)
    event_time = Column(BigInteger)
    event_date = Column(DateTime)
    ip = Column(String(32), default=None)
    id = Column(BigInteger, primary_key=True, autoincrement=True)


class UserLogout(Base):
    """
    user logout log
    """
    __tablename__ = 'UserLogout'
    user_id = Column(BigInteger, default=None)
    event_time = Column(BigInteger)
    event_date = Column(DateTime)
    ip = Column(String(32), default=None)
    id = Column(BigInteger, primary_key=True, autoincrement=True)


class UserLogin(Base):
    """
    user login log
    """
    __tablename__ = 'UserLogin'
    user_id = Column(BigInteger, default=None)
    event_time = Column(BigInteger)
    event_date = Column(DateTime)
    ip = Column(String(32), default=None)
    id = Column(BigInteger, primary_key=True, autoincrement=True)


class UserMsg(Base):
    """
    user message
    """
    __tablename__ = 'UserMsg'

    sender_id = Column(BigInteger, index=True)
    receiver_id = Column(BigInteger, index=True)
    create_time = Column(DateTime)
    # message main text
    msg_text = Column(Text)
    # message type
    msg_type = Column(Integer)
    msg_title = Column(VARCHAR(16))
    read_state = Column(Integer)
    expire_time = Column(DateTime)
    id = Column(BigInteger, primary_key=True, autoincrement=True)


# class BugLogger(Base):


#     ...

class UserMapper(Base):
    """
    store Sql query of user data analysis
    mapper_pickle store the dumped class of SqlMapper.
    mark level 1 means normal, 2 mean important, 3 mean public
    """
    __tablename__ = 'UserMapper'

    mapper_id = Column(BigInteger, index=True)
    mapper_name = Column(VARCHAR(64))
    user_id = Column(BigInteger, index=True)
    create_time = Column(DateTime)
    mapper_pickle = Column(BLOB)
    mark_level = Column(Integer, default=1)
    id = Column(BigInteger, primary_key=True, autoincrement=True)


class MapperPage(Base):
    """
    store data pic page
    """
    __tablename__ = 'MapperPage'

    page_id = Column(Integer, index=True)
    page_name = Column(VARCHAR(16))
    create_time = Column(DateTime)
    create_user_id = Column(BigInteger)
    marked = Column(Integer)
    id = Column(BigInteger, primary_key=True, autoincrement=True)


class MapperAndPage(Base):
    """
    store the relationship of data analysis query and data pic page,
    there store not unique mapper page and data analysis query.
    """
    __tablename__ = 'MapperAndPage'

    page_id = Column(Integer, index=True)
    mapper_id = Column(BigInteger, index=True)
    create_user = Column(BigInteger, index=True)
    create_time = Column(DateTime)
    id = Column(BigInteger, primary_key=True, autoincrement=True)


Base.metadata.create_all(engine)
web_db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# create the root user and test user if not exist


root_user = Config.All_ARGS.get('root_user')
root_password = Config.All_ARGS.get('root_password')
test_user = Config.All_ARGS.get('test_user', 'test_user')
test_password = Config.All_ARGS.get('test_password', '123456')
if web_db_session.query(UserTab).filter_by(username=root_user).first() is None:
    hasher = hashlib.md5()
    hasher.update(root_password.encode('utf-8'))
    root_account = UserTab(username='root', grant_level=10, passwordMD5=hasher.hexdigest())
    web_db_session.add(root_account)
    web_db_session.commit()
    web_db_session.close()
    del hasher, root_account

if web_db_session.query(UserTab).filter_by(username=test_user).first() is None:
    hasher = hashlib.md5()
    hasher.update(test_password.encode('utf-8'))
    test_account = UserTab(username=test_user, grant_level=4, passwordMD5=hasher.hexdigest())
    web_db_session.add(test_account)
    web_db_session.commit()
    web_db_session.close()
    del hasher, test_account

del root_user, root_password, test_user, test_password
