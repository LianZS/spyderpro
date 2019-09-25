from spyderpro.port_connect.sql_connect import MysqlOperation
from spyderpro.port_connect.paramchecks import ParamTypeCheck


class Parent(MysqlOperation, ParamTypeCheck):
    pass
