class ParamTypeCheck():
    @staticmethod
    def type_check(param, param_type):
        """
        参数类型检查
        :rtype:
        :param param:
        :param param_type:
        :return:
        """
        assert isinstance(param, param_type), "the type of param is wrong"
