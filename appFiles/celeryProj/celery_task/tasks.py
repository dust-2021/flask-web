import datetime
import json
import time

import pymysql

from appFiles.sql.connectionPool import redis_pool
from appFiles.sql.databaseForData import web_data_session
import redis
from .celery_manage import celery
from configs import Config
from hashlib import md5
import simplejson
from appFiles.appTools.smtp import Smtp
import os
from functools import partial

account_config = celery.conf.get('target_mysql')
local_conn = partial(pymysql.connect, host=account_config.get('host', 'localhost'),
                     port=account_config.get('port', 3306),
                     user=account_config.get('username'),
                     password=account_config.get('password'),
                     database='web_data')


@celery.task()
def celery_mapper_executor(query: str, arg_list, info):
    """
    execute the sql query of a mapper, 
    :param query: sql query
    :param arg_list:
    :param info:
    :return: 
    """
    hasher = md5()
    final_query = query % arg_list
    hasher.update(final_query.encode('utf-8'))
    _text = hasher.hexdigest()

    data = {'info': info, 'data': [[]]}
    conn = redis.Redis(connection_pool=redis_pool)
    redis_memory = conn.get(f'celery_mapper_executor:{_text}')
    if redis_memory:
        conn.close()
        return json.loads(redis_memory)
    else:
        data_conn = local_conn()
        try:
            with data_conn.cursor() as cs:
                cs.execute(query, arg_list)
                resp = cs.fetchall()
                resp = [list(x) for x in resp]
                data['data'] = resp
                conn.setex(f'celery_mapper_executor:{_text}', Config.MAPPER_RESUL_REDIS_LIFETIME,
                           simplejson.dumps(data))
        except pymysql.Error as err:
            print(err)
        finally:
            data_conn.close()
            conn.close()
            return data


@celery.task()
def celery_email_sender(smtp_kwargs: dict, target_addr: list, title, msg):
    """
    send a email
    :param smtp_kwargs:
    :param target_addr:
    :param title:
    :param msg:
    :return:
    """
    mail = Smtp(**smtp_kwargs)
    mail.login()
    mail.send_email(target=target_addr, title=title, msg=msg)
    resp = {"type": smtp_kwargs.get('type_name'), "title": title, "target": target_addr,
            "datetime": datetime.datetime.now()}
    return simplejson.dumps(resp)


@celery.task()
def celery_test():
    time.sleep(20)
    return f'{datetime.datetime.now()}'
