"""
待处理内容数据
"""
import json
from sqlalchemy import Column, String, create_engine, Integer, Float, VARCHAR, Text, DateTime, BigInteger, Date, BLOB, \
    CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
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
    sql_database = 'web_data'
    sql_connector = 'pymysql'
    sql_pool_size = _conf['sqlalchemy_pool_size']
    sql_pool_recycle = _conf['sqlalchemy_pool_recycle']
    _engine = create_engine(sql_url % (sql_connector, sql_user, sql_password, sql_host, sql_database), pool_size=sql_pool_size,
                            pool_recycle=sql_pool_recycle)
    return _engine


Base = declarative_base()
engine = engine_generator()


class UserAttr(Base):
    """
    all attribute of user, this not mean the user of this web app,it means the data which we want to
    analysis.
    """
    __tablename__ = 'UserAttr'

    username = Column(VARCHAR(64), index=True)
    uid = Column(BigInteger)
    user_reg = Column(DateTime)
    total_pay = Column(Float)
    last_login = Column(DateTime)
    last_pay_date = Column(DateTime)
    last_pay_count = Column(Float)
    level = Column(Integer)
    country = Column(VARCHAR(5))
    avg_mon_pay = Column(Float)
    extend1 = Column(VARCHAR(12), default=None)
    extend2 = Column(VARCHAR(12), default=None)
    id = Column(BigInteger, primary_key=True, autoincrement=True)


class Event(Base):
    """
    all the attribute of event
    """
    __tablename__ = 'Event'

    event_name = Column(VARCHAR(16), index=True)
    event_time = Column(DateTime)
    username = Column(VARCHAR(32))
    uid = Column(Integer)
    total_pay = Column(Float)
    online_time = Column(Integer)
    level = Column(Integer)
    ip_addr = Column(VARCHAR(32))
    country_code = Column(VARCHAR(4))
    product_id = Column(Integer, index=True)
    pay_money = Column(Float)
    id = Column(BigInteger, primary_key=True, autoincrement=True)


class NameSpace(Base):
    """
    the chinese name of columns in UserAttr and Event
    """

    __tablename__ = 'NameSpace'

    database_name = Column(VARCHAR(16))
    table_name = Column(VARCHAR(16))
    column_name = Column(VARCHAR(16))
    custom_name = Column(VARCHAR(32), default=None)
    column_type = Column(VARCHAR(16))
    column_type_custom = Column(Integer, default=None)
    mark_label = Column(Integer, default=0)
    id = Column(BigInteger, primary_key=True, autoincrement=True)


Base.metadata.create_all(engine)
web_data_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# initialization the columns name space of analysis data;
if web_data_session.execute('select count(*) from NameSpace;').first()[0] == 0:
    query = "show columns from %s;"
    user_attr_columns = web_data_session.execute(query % UserAttr.__tablename__).fetchall()
    for item in user_attr_columns:
        namespace = NameSpace(database_name='web_data', table_name=UserAttr.__tablename__, column_name=item[0],
                              column_type=item[1])
        web_data_session.add(namespace)
    event_columns = web_data_session.execute(query % Event.__tablename__).fetchall()
    for item in event_columns:
        namespace = NameSpace(database_name='web_data', table_name=Event.__tablename__, column_name=item[0],
                              column_type=item[1])
        web_data_session.add(namespace)
    web_data_session.commit()
    web_data_session.close()
    del query, user_attr_columns, namespace, event_columns, item
