import json
import re


class Connect:
    def connect(self, par: str, url: str) -> dict:
        """网络连接
        :param par:正则表达式
        :param url:请求链接
        :return json
        """


        data = self.request.get(url=url, headers=self.headers)
        if data.status_code != 200:
            print("%s请求--error:网络出错" % url)
            raise ConnectionError('网络连接中断')
        try:
            if par is not None:
                result = re.findall(par, data.content.decode('gbk'), re.S)[0]
            else:
                result = data.text
        except UnicodeDecodeError:
            result = re.findall(par, data.text, re.S)[0]

        data = json.loads(result)
        assert isinstance(data, (dict, list))
        return data
