connect(self, par: str, url: str)：实现网络链接

        :param par:正则表达式
        :param url:请求链接
        :return json
        请求参数par为正则表达式，参数url表示请求的网络链接
                         ，请求成功则返回json格式数据，否则抛出ConnectionError