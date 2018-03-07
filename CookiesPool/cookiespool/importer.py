import requests

from cookiespool.db import AccountRedisClient

conn = AccountRedisClient(name='weibo')

def set(account, sep='----'):
    username, password = account.split(sep)
    result = conn.set(username, password)
    print('account', username, 'password', password)
    print('success' if result else 'failed')


def scan():
    print('input user name and password, exit to exit')
    while True:
        account = input()
        if account == 'exit':
            break
        set(account)


if __name__ == '__main__':
    scan()
