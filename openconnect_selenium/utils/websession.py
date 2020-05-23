import os
import sys
import logging

from time import sleep
from asyncio import sleep as a_sleep

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from openconnect_selenium.utils.chromedriver import search_driver_in_path
from openconnect_selenium.utils.chromedriver import get_chromedriver

logger = logging.getLogger('oc.websession')


class Session:
    driver = None

    def __init__(
            self,
            url,
            user_data_dir=None,
            cookie_name=None
    ):
        self.url = url
        self.user_data_dir = user_data_dir
        self.cookie_name = cookie_name if cookie_name else 'DSID'
        logger.debug('searched cookie-name: {}'.format(self.cookie_name))

    @property
    def data_dir(self):
        if self.user_data_dir:
            return self.user_data_dir

        home = os.path.expanduser('~')

        return os.path.join(home, '.config/openconnect-selenium')

    def loop_wait_cookie(self):
        cookie = (None, None)

        self.driver.get(self.url)
        sleep(1)
        self.driver.refresh()
        sleep(2)
        try:
            while not [i for i in self.driver.get_cookies() if i.get('name', '') == self.cookie_name]:
                logger.info('waiting for cookie')
                sleep(2)
        except (WebDriverException, TypeError):
            logger.error('couldn\'t find cookie - Browser closed?')
            self.driver.quit()
            sys.exit(94)

        for i in self.driver.get_cookies():
            if not i.get('name', '') == self.cookie_name:
                continue
            cookie = (i['name'], i.get('value'))
            logger.debug('Cookie found: {}'.format(cookie))
            break

        return cookie

    async def wait_cookie_sync(self, time2wait=10):
        self.driver.minimize_window()
        await a_sleep(time2wait)
        self.driver.quit()


class ChromeSession(Session):
    def __init__(
            self,
            url,
            user_data_dir=None,
            cookie_name=None
    ):
        super().__init__(
            url=url,
            user_data_dir=user_data_dir,
            cookie_name=cookie_name
        )

        self.driver_chrome = None

    def _get_check_chromedriver(self):
        chromedriver = search_driver_in_path()
        chromedriver = chromedriver if chromedriver else get_chromedriver()
        logger.debug('Chromedriver is in path: {}'.format(chromedriver))

        return chromedriver

    @property
    def options(self):
        udd_str = 'user-data-dir={}-chrome'.format(self.data_dir)
        logger.debug(udd_str)
        out = webdriver.ChromeOptions()
        out.add_argument(udd_str)
        out.add_experimental_option('excludeSwitches', ['enable-automation'])

        return out

    @property
    def driver(self):
        try:
            self.driver_chrome = webdriver.Chrome(
                executable_path=self._get_check_chromedriver(),
                options=self.options
            ) if not self.driver_chrome else self.driver_chrome
        except WebDriverException as e:
            logger.error('cannot run webdriver - MESSAGE: "{}"'.format(str(e).replace('\n', '')))
            sys.exit(93)

        return self.driver_chrome
