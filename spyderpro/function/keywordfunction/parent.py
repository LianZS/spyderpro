from spyderpro.port_connect.sqlconnect import MysqlOperation
from spyderpro.port_connect.paramchecks import ParamTypeCheck


class Parent(MysqlOperation, ParamTypeCheck):
    pass
