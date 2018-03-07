import json

import requests
import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from cookiespool.config import *
from cookiespool.db import CookiesRedisClient, AccountRedisClient
from cookiespool.verify import Yundama


class CookiesGenerator(object):
    def __init__(self, name='default', browser_type=DEFAULT_BROWSER):
        """
        
        :param name:
        :param browser:  None
        """
        self.name = name
        self.cookies_db = CookiesRedisClient(name=self.name)
        self.account_db = AccountRedisClient(name=self.name)
        self.browser_type = browser_type

    def _init_browser(self, browser_type):
        """
       
        :param browser: default PhantomJS/ Chrome
        :return:
        """
        if browser_type == 'PhantomJS':
            caps = DesiredCapabilities.PHANTOMJS
            caps[
                "phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
            self.browser = webdriver.PhantomJS(desired_capabilities=caps)
            self.browser.set_window_size(1400, 500)
        elif browser_type == 'Chrome':
            self.browser = webdriver.Chrome()

    def new_cookies(self, username, password):
        raise NotImplementedError

    def set_cookies(self, account):
        """
       
        :param account:
        :return:
        """
        results = self.new_cookies(account.get('username'), account.get('password'))
        if results:
            username, cookies = results
            print('Saving Cookies to Redis', username, cookies)
            self.cookies_db.set(username, cookies)


    def run(self):
        """
        
        :return:
        """
        accounts = self.account_db.all()
        cookies = self.cookies_db.all()
        # Account user
        accounts = list(accounts)
        # Cookies user
        valid_users = [cookie.get('username') for cookie in cookies]
        print('Getting', len(accounts), 'accounts from Redis')
        if len(accounts):
            self._init_browser(browser_type=self.browser_type)
        for account in accounts:
            if not account.get('username') in valid_users:
                print('Getting Cookies of ', self.name, account.get('username'), account.get('password'))
                self.set_cookies(account)
        print('Generator Run Finished')

    def close(self):
        try:
            print('Closing Browser')
            self.browser.close()
            del self.browser
        except TypeError:
            print('Browser not opened')


class WeiboCookiesGenerator(CookiesGenerator):
    def __init__(self, name='weibo', browser_type=DEFAULT_BROWSER):
        """
        
        :param name:
        :param browser:
        """
        CookiesGenerator.__init__(self, name, browser_type)
        self.name = name
        self.ydm = Yundama(YUNDAMA_USERNAME, YUNDAMA_PASSWORD, YUNDAMA_APP_ID, YUNDAMA_APP_KEY)

    def _success(self, username):
        wait = WebDriverWait(self.browser, 5)
        success = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'me_portrait_w')))
        if success:
            print('success')
            self.browser.get('http://weibo.cn/')

            if "我的首页" in self.browser.title:
                print(self.browser.get_cookies())
                cookies = {}
                for cookie in self.browser.get_cookies():
                    cookies[cookie["name"]] = cookie["value"]
                print(cookies)
                print('get Cookies')
                return (username, json.dumps(cookies))

    def new_cookies(self, username, password):
        """
        生成Cookies
        :param username:
        :param password:
        :return: user name & Cookies
        """
        print('Generating Cookies of', username)
        self.browser.delete_all_cookies()
        self.browser.get('http://my.sina.com.cn/profile/unlogin')
        wait = WebDriverWait(self.browser, 20)

        try:
            login = wait.until(EC.visibility_of_element_located((By.ID, 'hd_login')))
            login.click()
            user = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginformlist input[name="loginname"]')))
            user.send_keys(username)
            psd = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginformlist input[name="password"]')))
            psd.send_keys(password)
            submit = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.login_btn')))
            submit.click()
            try:
                result = self._success(username)
                if result:
                    return result
            except TimeoutException:
                print('verify crc')
                yzm = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginform_yzm .yzm')))
                url = yzm.get_attribute('src')
                cookies = self.browser.get_cookies()
                cookies_dict = {}
                for cookie in cookies:
                    cookies_dict[cookie.get('name')] = cookie.get('value')
                response = requests.get(url, cookies=cookies_dict)
                result = self.ydm.identify(stream=response.content)
                if not result:
                    print('crc failed, skip ')
                    return
                door = wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginform_yzm input[name="door"]')))
                door.send_keys(result)
                submit.click()
                result = self._success(username)
                if result:
                    return result
        except WebDriverException as e:
            print(e.args)


class MWeiboCookiesGenerator(CookiesGenerator):
    def __init__(self, name='weibo', browser_type=DEFAULT_BROWSER):
        """
        
        :param name:
        :param browser:
        """
        CookiesGenerator.__init__(self, name, browser_type)
        self.name = name
        self.ydm = Yundama(YUNDAMA_USERNAME, YUNDAMA_PASSWORD, YUNDAMA_APP_ID, YUNDAMA_APP_KEY)

    def _success(self, username):
        wait = WebDriverWait(self.browser, 5)
        success = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'me_portrait_w')))

        if success:
            print('success')
            self.browser.get('http://m.weibo.cn/')

            if "weibo" in self.browser.title:
                print(self.browser.get_cookies())
                cookies = {}
                for cookie in self.browser.get_cookies():
                    cookies[cookie["name"]] = cookie["value"]
                print(cookies)
                print('get Cookies')
                return (username, json.dumps(cookies))

    def new_cookies(self, username, password):
        """
        generate Cookies
        :param username:
        :param password:
        :return:
        """
        print('Generating Cookies of', username)
        self.browser.delete_all_cookies()
        self.browser.get('http://my.sina.com.cn/profile/unlogin')
        wait = WebDriverWait(self.browser, 20)

        try:
            login = wait.until(EC.visibility_of_element_located((By.ID, 'hd_login')))
            login.click()

            user = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginformlist input[name="loginname"]')))
            user.send_keys(username)
            psd = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginformlist input[name="password"]')))
            psd.send_keys(password)
            submit = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.login_btn')))
            submit.click()
            try:
                result = self._success(username)
                if result:
                    return result
            except TimeoutException:
                print('verify crc')
                yzm = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginform_yzm .yzm')))
                url = yzm.get_attribute('src')
                cookies = self.browser.get_cookies()

                cookies_dict = {}
                for cookie in cookies:
                    cookies_dict[cookie.get('name')] = cookie.get('value')
                response = requests.get(url, cookies=cookies_dict)
                result = self.ydm.identify(stream=response.content)
                if not result:
                    print('crc failed, skip')
                    return
                door = wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginform_yzm input[name="door"]')))
                door.send_keys(result)
                submit.click()
                result = self._success(username)
                if result:
                    return result
        except WebDriverException as e:
            pass


if __name__ == '__main__':
    generator = WeiboCookiesGenerator()
    generator._init_browser('Chrome')
    generator.new_cookies('15197170054', 'gmwkms222')
