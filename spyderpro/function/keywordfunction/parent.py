from spyderpro.portconnect.sqlconnect import MysqlOperation
from spyderpro.portconnect.paramchecks import ParamTypeCheck


class Parent(MysqlOperation, ParamTypeCheck):
    pass
