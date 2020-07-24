import os
import sys
import zipfile
import logging

from urllib.request import urlopen
from urllib.error import HTTPError
from stat import S_IXUSR
from io import BytesIO
from subprocess import check_output
from shutil import which

ZIP_UNIX_SYSTEM = 3
logger = logging.getLogger('oc.chromedriver')


def extract_all_with_executable_permission(zf, target_dir):
    for info in zf.infolist():
        logger.debug('extracting "{}" to "{}"'.format(info.filename, target_dir))
        extracted_path = zf.extract(info, target_dir)

        if info.create_system == ZIP_UNIX_SYSTEM and os.path.isfile(extracted_path):
            unix_attributes = info.external_attr >> 16
            if unix_attributes & S_IXUSR:
                logger.debug('making "{}" executable'.format(extracted_path))
                os.chmod(extracted_path, os.stat(extracted_path).st_mode | S_IXUSR)


def search_driver_in_path():
    for path in os.environ['PATH'].split(os.pathsep):
        exe_file = os.path.join(path, 'chromedriver')
        if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
            return exe_file
    return None


def try_get_chrome_version(custom_name=None):
    chrome_names = [
        'google-chrome',
        'google-chrome-stable',
        'google-chrome-testing',
        'chrome',
        'chromium',
        'chromium-stable',
        'chromium-testing'
    ]

    if custom_name:
        chrome_names.append(custom_name)

    logger.debug(f'searching for the following binaries: {chrome_names}')

    for chrome_name in chrome_names:
        path = which(chrome_name)
        if path:
            logger.debug(f'found binary at {path}')
            version = check_output([path, '--version'])
            if not version:
                continue
            version = version.decode().replace(' \n', '').rsplit(' ', 1)[1].rsplit('.', 1)[0]
            return f'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version}'

    return 'http://chromedriver.storage.googleapis.com/LATEST_RELEASE'


def get_chromedriver(custom_name=None):
    chromedriver_path = '/tmp/chromedriver/chromedriver'
    latest_url = try_get_chrome_version(custom_name=custom_name)
    download_url = 'http://chromedriver.storage.googleapis.com/{}/chromedriver_linux64.zip'

    try:
        latest = urlopen(latest_url).read()
        logger.debug('latest found chromedriver version is "{}"'.format(latest.decode()))
    except HTTPError as e:
        logger.debug('getting latest chromedriver version not possible - {}'.format(e))
        sys.exit(91)

    try:
        logger.debug('download url is "{}"'.format(download_url.format(latest.decode())))
        download = urlopen(download_url.format(latest.decode())).read()
    except HTTPError as e:
        logger.error('getting chromedriver not possible - {}'.format(e))
        sys.exit(92)

    chromedriver_zip = BytesIO()
    chromedriver_zip.write(download)

    extract_all_with_executable_permission(zipfile.ZipFile(chromedriver_zip), '/tmp/chromedriver')

    return chromedriver_path
