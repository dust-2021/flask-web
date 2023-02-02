import time
import json
from celery import Celery
import os
from kombu import Exchange, Queue


def configs_generate():
    if os.path.isfile('appFiles/configTemp/appLoadConfig/personalAccount.json'):
        f = open('appFiles/configTemp/appLoadConfig/personalAccount.json', encoding='utf-8')
        _account_config = json.load(f)
        f.close()
    else:
        f = open('appFiles/configTemp/appLoadConfig/account.json', encoding='utf-8')
        _account_config = json.load(f)
        f.close()
    with open('appFiles/configTemp/appLoadConfig/celeryConfigs.json', 'r', encoding='utf-8') as f:
        _configs = json.load(f)
    celery_conf = {}
    if _configs.get('celery_env', 'default') == 'default':
        celery_conf = _configs.get('celery_configs')
    if _configs.get('celery_env', 'default') == 'development':
        celery_conf = _configs.get('celery_development_configs')
    if _configs.get('celery_env', 'default') == 'product':
        celery_conf = _configs.get('celery_product_configs')
    redis_account = _account_config.get('redis_conf') if celery_conf.get(
            'celery_mem') == 'remote' else _account_config.get('redis_local_conf')
    return redis_account, celery_conf


account_config, configs = configs_generate()

_broker_url = 'redis://:%s@%s:%s/%s' % (
    account_config.get('password'), account_config.get('host'), account_config.get('port'), 1)
_backend_url = 'redis://:%s@%s:%s/%s' % (
    account_config.get('password'), account_config.get('host'), account_config.get('port'), 2)

celery = Celery(__name__, broker=_broker_url, backend=_backend_url,
                include=['appFiles.celeryProj.celery_task.tasks'])
celery.conf.update(**configs)
