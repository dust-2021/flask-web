"""
api for data analysis and mapper generate
"""
from sqlalchemy import func
from flask import session, jsonify, request, Blueprint
from appFiles.appTools.others import session_check, grant_checker
from appFiles.sql.databaseForWeb import *
from appFiles.sql.databaseForData import *
from appFiles.sql.mapper_generator import EchartsGenerator
from appFiles.sql.mapper_generator import SqlMapper
from appFiles.celeryProj.celery_task.celery_manage import celery
from appFiles.celeryProj.celery_task.tasks import celery_mapper_executor, celery_test
from celery.result import AsyncResult
from configs import DataConfig
from hashlib import md5
import math

sql_mapper = Blueprint('sql_mapper', __name__)


@sql_mapper.route('/mapper', methods=['POST'])
@session_check
def mapper():
    """
    accept the options of custom data analysis, then return sql query.
    :return:
    """
    opts = request.json
    the_mapper = SqlMapper(**opts)
    # conn = redis.Redis(connection_pool=redis_pool)
    # conn.set()
    # conn.close()
    return the_mapper.dump()


@sql_mapper.route('/mapper/store', methods=['POST'])
@session_check
def store_mapper():
    resp = {
        'status': None,
        'message': None
    }

    opts = request.json
    title = opts.get('title')
    _mapper = SqlMapper(**opts)
    user_id = session.get('user_id')
    res = web_db_session.query(func.max(UserMapper.mapper_id)).first()
    mapper_id = res[0] + 1 if res[0] else 1
    user_mapper = UserMapper(mapper_id=mapper_id, mapper_name=title, user_id=user_id,
                             create_time=datetime.datetime.now(), mapper_pickle=_mapper.dump(), mark_level=0)
    web_db_session.add(user_mapper)
    web_db_session.commit()
    web_db_session.close()
    resp['status'] = 'SUCCESS'
    return jsonify(resp)


@sql_mapper.route('/mapper/mapper_executor', methods=['POST'])
@session_check
def mapper_executor():
    opts = request.json
    _mapper = SqlMapper(**opts)
    _info = {
        'target_table': _mapper.target_table,
        'group_column_count': _mapper.group_by.__len__(),
        'rename': _mapper.rename
    }

    task_id = celery_mapper_executor.delay(_mapper.query, tuple(_mapper.arg_dict), _info).id
    resp = {
        'state': 'success',
        'task_id': task_id,
        'task_time': datetime.datetime.timestamp(datetime.datetime.now()),
        'result': None
    }
    return jsonify(resp)


@sql_mapper.route('/mapper/mapper_result/<task_id>')
@session_check
def mapper_result(task_id):
    """
    update a celeryProj id of celery work, then wait till result data yield and return result.
    param task_id: celery work id
    :return: json result
    """
    result = AsyncResult(task_id, app=celery).get()
    _gen = EchartsGenerator(result.get('data'), result.get('info'))
    return jsonify(_gen.opts)


@sql_mapper.route('/mapper/mapper_status/<task_id>')
@session_check
def mapper_status(task_id):
    status = AsyncResult(task_id, app=celery).status
    resp = {
        'id': task_id,
        'status': status
    }
    return jsonify(resp)


@sql_mapper.route('/columns', methods=['GET'])
@session_check
def columns():
    """
    return all columns of data
    :return:
    """
    resp = web_data_session.query(NameSpace.database_name, NameSpace.table_name, NameSpace.column_name,
                                  NameSpace.custom_name,
                                  NameSpace.column_type, NameSpace.column_type_custom, NameSpace.mark_label,
                                  NameSpace.id).all()
    web_data_session.close()
    resp = [{'database_name': x[0], 'table_name': x[1], 'column_name': x[2], 'custom_name': x[3],
             'column_type': x[4], 'column_type_custom': x[5], 'mark_label': x[6], 'column_id': x[7]} for x in resp]
    return jsonify(resp)


@sql_mapper.route('/columns/page/<int:page_num>')
@session_check
def column_page(page_num):
    resp = web_data_session.query(NameSpace.database_name, NameSpace.table_name, NameSpace.column_name,
                                  NameSpace.custom_name,
                                  NameSpace.column_type, NameSpace.column_type_custom, NameSpace.mark_label,
                                  NameSpace.id).limit(10).offset((page_num - 1) * 10).all()
    _pages = math.ceil(web_data_session.query(func.count(NameSpace.id)).first()[0] / 10)
    web_data_session.close()
    resp = {'all_page': _pages,
            'data': [{'database_name': x[0], 'table_name': x[1], 'column_name': x[2], 'custom_name': x[3],
                      'column_type': x[4], 'column_type_custom': x[5], 'mark_label': x[6], 'column_id': x[7]} for x in
                     resp]}

    return jsonify(resp)


@sql_mapper.route('/columns/type')
@session_check
def columns_type():
    """
    api for columns' type and group func of columns
    :return: [{}, ...]
    """
    resp = web_data_session.query(NameSpace.column_name, NameSpace.id, NameSpace.column_type_custom,
                                  NameSpace.custom_name).all()
    web_data_session.close()
    response_data = []
    for _item in resp:
        response_data.append(
            {'column_name': _item[3] if _item[3] else _item[0], 'column_id': _item[1], 'column_type_custom': _item[2]})
    return jsonify(response_data)


@sql_mapper.route('/columns/type/<string:table_name>')
@session_check
def column_type_table(table_name):
    resp = web_data_session.query(NameSpace.column_name, NameSpace.id, NameSpace.column_type_custom,
                                  NameSpace.custom_name).filter_by(table_name=table_name).all()
    web_data_session.close()
    response_data = []
    for _item in resp:
        response_data.append(
            {'column_name': _item[3] if _item[3] else _item[0], 'column_id': _item[1], 'column_type_custom': _item[2]})
    return jsonify(response_data)


@sql_mapper.route('/columns/group_func/<column_id>')
@session_check
def column_group_func(column_id):
    if not column_id:
        return jsonify(list())
    _type = web_data_session.query(NameSpace.column_type_custom).filter_by(id=column_id).first()
    # means column id not exist
    if not _type:
        return jsonify(list())
    # means the column custom type haven't been set
    if not _type[0]:
        resp = DataConfig.COLUMNS_GROUP_FUNCS['0']
        return jsonify(resp)
    resp = DataConfig.COLUMNS_GROUP_FUNCS.get(str(_type[0]), list())
    return jsonify(resp)


@sql_mapper.route('/columns/condition_type')
@session_check
def all_column_condition_type():
    return jsonify(DataConfig.COLUMNS_CONDITION_TYPES)


@sql_mapper.route('/columns/relation_func')
@session_check
def all_column_relation_func():
    return jsonify(DataConfig.COLUMNS_RELATIONSHIP_FUNCS)


@sql_mapper.route('/columns/modify', methods=['GET', 'POST'])
@session_check
@grant_checker(4)
def modify_column():
    """
    modify info of columns, posted parameter:
    column_name: type-str, name of column in database.
    custom_name: type-str, nickname of column.
    column_type_custom: type-str or int, 0 means text, 1 means number, 2 means datetime.
    :return:
    """
    req = request.form
    resp = {'status': None, 'message': None}
    column_id, column_name, custom_name, column_type_custom = req.get('column_id'), req.get('column_name'), req.get(
        'custom_name'), req.get('column_type_custom', 0)
    if len(custom_name) > 32:
        resp['status'] = 'failed'
        resp['message'] = '名称需小于32个字符'
        return jsonify(resp)

    try:
        web_data_session.query(NameSpace).filter_by(id=column_id).update(
            {NameSpace.custom_name: custom_name if custom_name else column_name,
             NameSpace.column_type_custom: column_type_custom})
        resp['status'] = 'success'
    except Exception as err:
        resp['message'] = err.__repr__()
        resp['status'] = 'failed'
        web_data_session.rollback()
    finally:
        web_data_session.commit()
        web_data_session.close()
    return jsonify(resp)


@sql_mapper.route('/columns/mark/<int:column_id>')
@session_check
def mark_column(column_id):
    """
    change a column's mark
    """
    result = web_data_session.query(NameSpace.mark_label).filter_by(id=column_id).first()
    if not result:
        return 'ERROR'
    if result[0]:
        ...
