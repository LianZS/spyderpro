import requests
import json
import re


class Connect:
    def connect(self, par, url: str) -> dict:
        """网络连接"""
        '''返回json数据'''
        data = self.request.get(url=url, headers=self.headers)
        if data.status_code != 200:
            print("%s请求--error:网络出错" % url)
            raise ConnectionError('网络连接中断')
        try:
            result = re.findall(par, data.content.decode('gbk'), re.S)
        except UnicodeDecodeError:
            result = re.findall(par, data.text, re.S)

        data = json.loads(result[0])
        assert isinstance(data, dict)
        return data
