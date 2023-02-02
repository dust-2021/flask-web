from appFiles.sql.databaseForData import *
from appFiles.sql.databaseForWeb import *
from sqlalchemy.sql import func


class AnalysisDataTools:

    def __init__(self):
        ...

    @staticmethod
    def get_analysis_column_name_by_id(column_id: int):
        """
        get column name by given id
        :param column_id:
        :return:
        """
        result = web_data_session.query(NameSpace.column_name).filter_by(id=column_id).first()
        web_data_session.close()
        if result:
            return result[0]
        else:
            return None

    @staticmethod
    def get_analysis_column_name_by_id_list(column_id_list: list):
        result = web_data_session.query(NameSpace.id, NameSpace.column_name).filter(
            NameSpace.id.in_(column_id_list)).all()
        if result:
            return dict(result)
        else:
            return None


class WebDataTools:
    def __init__(self):
        ...
