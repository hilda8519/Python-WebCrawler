import random

import redis

from cookiespool.config import *
from cookiespool.error import *


class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化Redis
        :param host:
        :param port:
        :param password:
        """
        if password:
            self._db = redis.Redis(host=host, port=port, password=password)
        else:
            self._db = redis.Redis(host=host, port=port)
        self.domain = REDIS_DOMAIN
        self.name = REDIS_NAME

    def _key(self, key):
        """
        
        :param key:
        :return:
        """
        return "{domain}:{name}:{key}".format(domain=self.domain, name=self.name, key=key)

    def set(self, key, value):
        """
        
        :param key:
        :param value:
        :return:
        """
        raise NotImplementedError

    def get(self, key):
        """
        
        :param key:
        :return:
        """
        raise NotImplementedError

    def delete(self, key):
        """
        
        :param key:
        :return:
        """
        raise NotImplementedError

    def keys(self):
        """
        
        :return:
        """
        return self._db.keys('{domain}:{name}:*'.format(domain=self.domain, name=self.name))

    def flush(self):
        """
        
        :return:
        """
        self._db.flushall()


class CookiesRedisClient(RedisClient):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, domain='cookies', name='default'):
        """
        cookie
        :param host:
        :param port:
        :param password:
        :param domain: cookies, account
        :param name: weibo, default
        """
        RedisClient.__init__(self, host, port, password)
        self.domain = domain
        self.name = name

    def set(self, key, value):
        try:
            self._db.set(self._key(key), value)
        except:
            raise SetCookieError

    def get(self, key):
        try:
            return self._db.get(self._key(key)).decode('utf-8')
        except:
            return None

    def delete(self, key):
        try:
            print('Delete', key)
            return self._db.delete(self._key(key))
        except:
            raise DeleteCookieError

    def random(self):
        """
        Cookies
        :return:
        """
        try:
            keys = self.keys()
            return self._db.get(random.choice(keys))
        except:
            raise GetRandomCookieError

    def all(self):
        """
        
        :return:
        """
        try:
            for key in self._db.keys('{domain}:{name}:*'.format(domain=self.domain, name=self.name)):
                group = key.decode('utf-8').split(':')
                if len(group) == 3:
                    username = group[2]
                    yield {
                        'username': username,
                        'cookies': self.get(username)
                    }
        except Exception as e:
            print(e.args)
            raise GetAllCookieError

    def count(self):
        """
        get Cookies number
        :return: number
        """
        return len(self.keys())



class AccountRedisClient(RedisClient):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, domain='account', name='default'):
        RedisClient.__init__(self, host, port, password)
        self.domain = domain
        self.name = name

    def set(self, key, value):
        try:
            return self._db.set(self._key(key), value)
        except:
            raise SetAccountError

    def get(self, key):
        try:
            return self._db.get(self._key(key)).decode('utf-8')
        except:
            raise GetAccountError

    def all(self):
        """
        get all accounts
        :return:
        """
        try:
            for key in self._db.keys('{domain}:{name}:*'.format(domain=self.domain, name=self.name)):
                group = key.decode('utf-8').split(':')
                if len(group) == 3:
                    username = group[2]
                    yield {
                        'username': username,
                        'password': self.get(username)
                    }
        except Exception as e:
            print(e.args)
            raise GetAllAccountError

    def delete(self, key):
        """
       
        :param key:
        :return:
        """
        try:
            return self._db.delete(self._key(key))
        except:
            raise DeleteAccountError


if __name__ == '__main__':
    """
    conn = CookiesRedisClient()
    conn.set('name', 'Mike')
    conn.set('name2', 'Bob')
    conn.set('name3', 'Amy')
    print(conn.get('name'))
    conn.delete('name')
    print(conn.keys())
    print(conn.random())
    """
    # test
    conn = AccountRedisClient(name='weibo')
    conn2 = AccountRedisClient(name='mweibo')


    accounts = conn.all()
    for account in accounts:
        conn2.set(account['username'], account['password'])
