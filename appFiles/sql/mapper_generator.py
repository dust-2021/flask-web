from appFiles.appTools.error import *
from appFiles.sql.databaseForData import UserAttr, Event, web_data_session, NameSpace
from appFiles.sql.databaseTools import AnalysisDataTools
import pickle
from configs import DataConfig


class SqlMapper:
    """
    this class get the options of user custom data-analysis, then yield a Sql query for MySql,
    all the input option must be list, although there is only one arg

    select: the data user want to get. [{"column":"", "group_func":"", "rel_column":"",
    "rel_group_func":"", "relation_func": "", "rename": ""}, ...]

    target_table: str type, name of the data table.

    where: the select condition of the original data. [{"column":"", "condition_type":"",
    "condition":""}]

    having: the same list as `where` condition.


    """
    __group_func__ = ['count', 'avg', 'max', 'min', 'sum', 'std']
    __cal_func__ = ['round']
    __rel_func__ = ['+', '-', '*', '/']

    __target_table = [UserAttr.__tablename__, Event.__tablename__]

    __condition_type__ = DataConfig.COLUMNS_CONDITION_TYPES

    def __init__(self, **kwargs):
        self.select = kwargs.get('select', list())
        self.target_table = kwargs.get('target_table', Event.__tablename__)
        self.where = kwargs.get('where', list())
        self.group_by = kwargs.get('group_by', list())
        self.having = kwargs.get('having', list())
        self.order_by = kwargs.get('order_by', list())
        self.limit = kwargs.get('limit', 3000)
        # the final sql query after all formatted
        self.query = None
        self.arg_dict = []

        self.rename = [f'col_{x}' for x in range(len(self.select))]

        # change the group columns' name if group columns' type is a number
        if len(self.group_by) > 0:
            for i in range(self.group_by.__len__()):
                # change group column's id into name
                if isinstance(self.group_by[i], str):
                    continue
                else:
                    self.group_by[i] = AnalysisDataTools.get_analysis_column_name_by_id(int(self.group_by[i]))

        # yield the query into self.query
        self._all_format()

    @staticmethod
    def user_attr_name_space():
        col = web_data_session.query(NameSpace.table_name, NameSpace.column_name, NameSpace.custom_name,
                                     NameSpace.column_type,
                                     NameSpace.mark_label).filter_by(table_name=UserAttr.__tablename__).all()
        web_data_session.close()
        return [tuple(x) for x in col]

    @staticmethod
    def event_name_space():
        col = web_data_session.query(NameSpace.table_name, NameSpace.column_name, NameSpace.custom_name,
                                     NameSpace.column_type,
                                     NameSpace.mark_label).filter_by(table_name=Event.__tablename__).all()
        web_data_session.close()
        return [tuple(x) for x in col]

    def _columns_format(self) -> str:
        """
        format the columns from a dict args, which is user want to calculate
        :return: a part of the SQL query
        """
        _str = []
        if len(self.select) <= 0:
            raise AppError('there is no column selected!')

        i = 0
        for item in self.select:
            # get the main column and calculate column
            col_id, rel_col_id = item.get('column'), item.get('rel_column')
            column = AnalysisDataTools.get_analysis_column_name_by_id(int(col_id)) if col_id else None
            rel_column = AnalysisDataTools.get_analysis_column_name_by_id(int(rel_col_id)) if rel_col_id else None

            # set default group function as count
            column_group_func = item.get('group_func')
            column_group_func = column_group_func if column_group_func in self.__group_func__ else 'count'
            column_rel_group_func = item.get('rel_group_func')
            column_rel_group_func = column_rel_group_func if column_rel_group_func in self.__group_func__ else 'count'

            relation_func = item.get('relation_func')

            if not column:
                continue
            single_str = f'{column_group_func}({column})' if column_group_func != 'count_distinct' \
                else f'count(distinct {column})'

            # if there exist a related column, then add it.
            if rel_column:
                if relation_func not in self.__rel_func__:
                    raise AppError(f'not allowed relation func {relation_func}')

                rela_str = f' {column_rel_group_func}({rel_column})' if column_rel_group_func != 'count_distinct' \
                    else f'count(distinct {rel_column})'

                # concat the column and related column.
                single_str = f'{single_str} {relation_func} {rela_str}'

            single_str += f' as {"col_" + str(i)} '
            i += 1
            _str.append(single_str)

        resp = ','.join(_str)
        return resp

    def _condition_format(self):
        """
        format the select condition
        :return: a part of Sql query
        """
        if len(self.where) == 0:
            return ' '
        _str = []
        for item in self.where:
            column_id = item.get('column')
            column = AnalysisDataTools.get_analysis_column_name_by_id(column_id) if column_id else None
            condition_type = item.get('condition_type')
            condition = item.get('condition')

            if condition_type not in self.__condition_type__:
                raise AppError('unknown condition type')
            if not column:
                continue

            if condition_type == 'in' or condition_type == 'not in':
                in_item = condition.split(',')
                single_string = f' {column} {condition_type} ({",".join(["%s"] * len(in_item))})'
                self.arg_dict += list(in_item)
            else:
                single_string = f' {column} {condition_type} %s '
                self.arg_dict.append(condition)
            _str.append(single_string)
        return 'where ' + ' and '.join(_str)

    def _having_condition_format(self):
        """
        format the having condition
        :return: a part of Sql query
        """
        if len(self.having) == 0:
            return ' '
        _str = []
        for item in self.having:
            if item['condition_type'] not in self.__condition_type__:
                raise AppError('unknown condition type')

            # single_string = f'{item["column"]} {item["condition_type"]} {item["condition"]}'
            single_string = ' %s %s %s '
            self.arg_dict += [item["column"], item["condition_type"], item["condition"]]
            _str.append(single_string)
        return 'having ' + ' and '.join(_str)

    def _order_format(self):
        """
        custom order the result, but now it is not necessary to grant this function to normal user.
        :return:
        """
        _order_str = ' '

        _order_str += 'order by ' + ','.join([f' {self.rename[i]} desc ' for i in range(len(self.select))])
        return _order_str

    def _group_format(self):
        if len(self.group_by) == 0:
            group_part = ''
            group_front_part = ''
        else:
            group_part = ' group by ' + ','.join(self.group_by)
            group_front_part = ','.join(
                [f'{self.group_by[x]} as group_func{x}' for x in range(self.group_by.__len__())])
        return group_front_part, group_part

    def _all_format(self):
        """
        yield the final query, the query will be able to store
        :return:
        """
        select_part = self._columns_format()
        where_part = self._condition_format()
        group_front_part, group_part = self._group_format()
        having_part = self._having_condition_format()
        order_part = self._order_format()

        # concat every part of Sql query
        # query = self.__base_query__ % (select_part, self.target_table if self.target_table else Event.__tablename__) \
        #         + where_part + group_part + having_part + order_part + ' limit ' + str(self.limit) + ';'

        sql_query = f'select {group_front_part + "," if group_front_part else ""} {select_part} ' \
                    f'from {self.target_table} {where_part} {group_part} {having_part} {order_part} ;'

        self.query = sql_query

    def dump(self):
        resp = pickle.dumps(self)
        return resp

    @staticmethod
    def load(byte_like):
        obj = pickle.loads(byte_like)
        return obj


class EchartsGenerator:
    def __init__(self, data, info):
        self.data = data
        self.info = info
        self.opts = {
            'tooltip': {
                'show': True,
                'trigger': 'axis',
                'axisPointer': {
                    'type': 'shadow'
                }
            },
            'legend': {

            },
            'xAxis': [{
                'type': 'category',
                'data': []
            }],
            'yAxis': [{'type': 'value'}],
            'series': []
        }

        self.generate_by_result()
        self.generate_data_series()

    def generate_by_result(self):
        group_times = self.info.get('group_column_count', 0)

        group_result_name = ['-'.join([str(y) for y in x[:self.info.get('group_column_count')]]) for x in
                             self.data] if group_times else []
        self.opts['xAxis'][0]['data'] = group_result_name

    def generate_data_series(self):
        group_times = self.info.get('group_column_count', 0)
        series_name = self.info.get('rename')

        for i in range(group_times, self.data[0].__len__()):
            data_series = {
                'name': series_name[i - group_times],
                'type': 'bar',
                'stack': None,
                'label': {
                    'show': True
                },
                'data': [round(float(x[i]), 2) for x in self.data]
            }
            self.opts['series'].append(data_series)
