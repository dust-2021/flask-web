"""
insert random generate data into mysql,
"""
import datetime

import pymysql
from pymysql.constants import CLIENT
import random
from functools import partial
import hashlib
from appFiles.sql.databaseForData import UserAttr, Event
from appFiles.sql.databaseForWeb import UserMsg, UserTab, UserLogin, UserLogout, UserRegister

local_conn = partial(pymysql.connect, host='127.0.0.1',
                     user='flask_user', passwd='123456', db='flask_web', port=3306,
                     client_flag=CLIENT.MULTI_STATEMENTS)

data_conn = partial(pymysql.connect, host='127.0.0.1',
                    user='flask_user', passwd='123456', db='web_data', port=3306,
                    client_flag=CLIENT.MULTI_STATEMENTS)

str_random = """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&'()*+,-./:;?@[\]^_`{|}~"""
country_list = ['CN', 'UK', 'US', 'JP', 'KR', 'IT', 'CA', 'VN', 'FR', 'GE', 'SP']


def user_rand():
    length = random.randint(6, 16)
    username = ''.join([random.choice(str_random) for _ in range(length)])
    grant_level = random.randint(1, 5)
    passwordMD5 = ''.join([random.choice(str_random) for _ in range(length)])
    hasher = hashlib.md5()
    hasher.update(passwordMD5.encode('utf-8'))
    passwordMD5 = hasher.hexdigest()
    extendColumn = 'null'
    return username, str(grant_level), passwordMD5, extendColumn


def user_attr_rand():
    length = random.randint(6, 32)
    username = ''.join([random.choice(str_random) for _ in range(length)])
    uid = random.randint(0, 2 ** 31)
    user_reg = datetime.datetime.fromtimestamp(
        datetime.datetime.timestamp(datetime.datetime.now()) - random.randint(0, 3600 * 24 * 1000))
    total_pay = random.randint(0, 100000) + (random.randint(0, 100) / 100)
    last_login = datetime.datetime.fromtimestamp(
        datetime.datetime.timestamp(datetime.datetime.now()) - random.randint(0, 3600 * 24 * 10))
    last_pay_date = datetime.datetime.fromtimestamp(
        datetime.datetime.timestamp(datetime.datetime.now()) - random.randint(0, 3600 * 24 * 20))
    last_pay_count = random.randint(0, 1000) + (random.randint(0, 100) / 100)
    level = random.randint(1, 60)
    country = random.choice(country_list)
    avg_mon_pay = random.randint(0, 10000) + (random.randint(0, 100) / 100)
    return username, uid, user_reg, total_pay, last_login, last_pay_date, last_pay_count, level, country, avg_mon_pay


def random_insert():
    conn = data_conn()
    try:
        with conn.cursor() as cs:
            cs.executemany("""    
insert into UserAttr (username, uid,user_reg,total_pay,last_login,last_pay_date,last_pay_count,level,country,avg_mon_pay)
values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", [user_attr_rand() for _ in range(1000)])
    except pymysql.Error as err:
        print(err)
        conn.rollback()
    finally:
        conn.commit()
        conn.close()


if __name__ == '__main__':
    random_insert()
