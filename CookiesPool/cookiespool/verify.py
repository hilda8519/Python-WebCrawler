import time

import requests
from requests.exceptions import ConnectionError

from cookiespool.config import *


class Yundama():
    def __init__(self, username, password, app_id, app_key, api_url=YUNDAMA_API_URL):
        self.username = username
        self.password = password
        self.app_id = str(app_id) if not isinstance(app_id, str) else app_id
        self.app_key = app_key
        self.api_url = api_url

    def login(self):
        """
        登录云打码账户
        :return:
        """
        try:
            data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.app_id,
                    'appkey': self.app_key}
            response = requests.post(self.api_url, data=data)
            if response.status_code == 200:
                result = response.json()
                print(result)
                if 'ret' in result.keys() and result.get('ret') < 0:
                    return self.error(result.get('ret'))
                else:
                    return result
            return None
        except ConnectionError:
            return None

    def upload(self, files, timeout, code_type):
        """
        
        :param files:
        :param timeout:
        :param code_type:
        :return:
        """
        try:
            data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.app_id,
                    'appkey': self.app_key, 'codetype': str(code_type), 'timeout': str(timeout)}
            response = requests.post(self.api_url, data=data, files=files)
            if response.status_code == 200:
                return response.json()
            return None
        except ConnectionError:
            return None

    def retry(self, cid, try_count=1):
        """
               :param cid:
        :param try_count:
        :return: 
            """
        if try_count >= YUNDAMA_MAX_RETRY:
            return None
        print('Retrying: ', cid, 'Count: ', try_count)
        time.sleep(2)
        try:
            data = {'method': 'result', 'cid': cid}
            print(data)
            response = requests.post(self.api_url, data=data)
            if response.status_code == 200:
                result = response.json()
                print(result)
                if 'ret' in result.keys() and result.get('ret') < 0:
                    print(self.error(result.get('ret')))
                if result.get('ret') == 0 and 'text' in result.keys():
                    return result.get('text')
                else:
                    return self.retry(cid, try_count + 1)
            return None
        except ConnectionError:
            return None

    def identify(self, file=None, stream=None, timeout=60, code_type=5000):
        """
        
        :param file:
        :param stream:
        :param timeout:
        :param code_type:
        :return:
        """
        if stream:
            files = {'file': stream}
        elif file:
            files = {'file': open(file, 'rb')}
        else:
            return None
        result = self.upload(files, timeout, code_type)
        if 'ret' in result.keys() and result.get('ret') < 0:
            print(self.error(result.get('ret')))
        if result.get('text'):
            print('crc sucess', result.get('text'))
            return result.get('text')
        else:
            return self.retry(result.get('cid'))

    def error(self, code):
        """
        
        :param code:
        :return:
        """
        map = {
            -1001: 'wrong password',
            -1002: 'wrong ID',
            -1003: 'user block',
            -1004: 'IP block',
            -1005: 'software block',
            -1006: 'loggin IP does not match user ip',
            -1007: 'balance is 0',
            -2001: 'crc is wrong',
            -2002: 'crc pictures is too large',
            -2003: 'crc pictures is damaged',
            -2004: 'upload crc pic failed',
            -3001: 'ID does not exist	',
            -3002: 'crc is under verfication',
            -3003: 'crc verification time excced',
            -3004: 'crc can not figure out',
            -3005: 'crc failed to report wrong',
            -4001: 'gifted card is invalid',
            -5001: 'registation failed'
        }
        return 'yudama' + map.get(code)


if __name__ == '__main__':
    ydm = Yundama(YUNDAMA_USERNAME, YUNDAMA_PASSWORD, YUNDAMA_APP_ID, YUNDAMA_APP_KEY)
    result = ydm.identify(file='getimage.jpg')
    print(result)
