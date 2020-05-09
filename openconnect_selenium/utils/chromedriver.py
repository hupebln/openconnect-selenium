import os
import sys
import zipfile
import logging

from urllib.request import urlopen
from urllib.error import HTTPError
from stat import S_IXUSR
from io import BytesIO

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


def get_chromedriver():
    chromedriver_path = '/tmp/chromedriver/chromedriver'
    latest_url = 'http://chromedriver.storage.googleapis.com/LATEST_RELEASE'
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
