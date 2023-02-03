import datetime
import json
import os
import random

from pytz import timezone

from redis import Redis

work_path = os.getcwd()


def load_config_file():
    """
    load configs from config json file.
    :return:
    """
    if os.path.isfile('appFiles/configTemp/appLoadConfig/personalAccount.json'):
        f = open('appFiles/configTemp/appLoadConfig/personalAccount.json', encoding='utf-8')
        _account_config = json.load(f)
        f.close()
    else:
        f = open('appFiles/configTemp/appLoadConfig/account.json', encoding='utf-8')
        _account_config = json.load(f)
        f.close()
    f = open('appFiles/configTemp/appLoadConfig/appConfigFile.json', encoding='utf-8')
    configs = json.load(f)
    f.close()

    f = open('appFiles/configTemp/appLoadConfig/dataConfig.json', encoding='utf-8')
    _data_config = json.load(f)['data_config']
    f.close()

    _app_config = None
    print(f'[{datetime.datetime.now()}] App running environment: {configs["app_env"]}')

    if configs['app_env'] == 'default':
        _app_config = configs['app_configs']
    elif configs['app_env'] == 'development':
        _app_config = configs['app_development_configs']
    elif configs['app_env'] == 'production':
        _app_config = configs['app_production_configs']
    elif configs['app_env'] == 'test':
        _app_config = configs['app_test_configs']

    env_values = configs['env_values']
    for item in env_values.keys():
        os.environ[item] = env_values.get(item)

    del env_values

    return _account_config, _app_config, _data_config


account_config, app_config, data_config = load_config_file()


class Config(object):
    """
    app base config
    """

    SECRET_KEY = app_config.get('app_secret_key', 'nothing')
    SESSION_TYPE = app_config.get('session_type', 'file')
    redis_account = None
    if app_config.get('session_mem') == 'remote':
        redis_account = account_config.get('redis_conf')
    if app_config.get('session_mem') == 'local':
        redis_account = account_config.get('redis_local_conf')

    SESSION_REDIS = Redis(host=redis_account.get('host'), port=redis_account.get('port', 6379),
                          password=redis_account.get('password'), db=0)
    REDIS_ARGS = redis_account

    REDIS_EXPIRE = app_config.get('redis_expire', 3600 * 24)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = app_config.get('permanent_session_lifetime', 3600 * 2)

    JSON_AS_ASCII = False

    SCHEDULER_TIMEZONE = timezone(app_config.get('scheduler_timezone'))
    SCHEDULER_API_ENABLED = app_config.get('scheduler_api_enabled', False)

    # custom configs
    MAPPER_RESUL_REDIS_LIFETIME = app_config.get('mapper_result_redis_lifetime', 1800)

    All_ARGS = app_config

    SQLALCHEMY_MEM = app_config.get('sqlalchemy_mem', 'local')
    # SQLALCHEMY_POOL_SIZE = app_config.get('sqlalchemy_pool_size')
    # SQLALCHEMY_POOL_TIMEOUT = app_config.get('sqlalchemy_pool_timeout')
    # SQLALCHEMY_POOL_RECYCLE = app_config.get('sqlalchemy_pool_recycle')
    # SQLALCHEMY_URL = app_config.get('sqlalchemy_database_url')

    def __init__(self):
        pass


class DataConfig:
    COLUMNS_GROUP_FUNCS = data_config.get('columns_group_funcs')
    COLUMNS_RELATIONSHIP_FUNCS = data_config.get('columns_relationship_funcs')
    COLUMNS_CONDITION_TYPES = data_config.get('columns_condition_types')

    @classmethod
    def reload_config(cls):
        new_conf = load_config_file()[1]
        cls.COLUMNS_GROUP_FUNCS = new_conf.get('columns_group_funcs')
        cls.COLUMNS_RELATIONSHIP_FUNCS = new_conf.get('columns_relationship_funcs')
        cls.COLUMNS_CONDITION_TYPES = new_conf.get('columns_condition_types')


del app_config, data_config
