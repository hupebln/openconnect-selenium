#!/usr/bin/env python

import argparse
import re
import sys
import asyncio
import signal
import logging

from openconnect_selenium.utils.websession import ChromeSession
from openconnect_selenium.utils.openconnect import run_openconnect
from openconnect_selenium.utils.openconnect import stop_vpn

__author__ = "Christian Schirge"
__copyright__ = "Copyright 2020, Christian Schirge"
__license__ = "MIT"
__version__ = "0.0.8"
__maintainer__ = "Christian Schirge"
__status__ = "Testing"

logger = logging.getLogger('oc')


class ProtoException(Exception):
    pass


def prepare_logger(level):
    log_level = logging.getLevelName(level)
    log_level = log_level if type(log_level) == int else logging.ERROR
    logger.setLevel(log_level)
    stream_formatter = logging.Formatter('%(levelname)s - %(message)s')
    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(stream_formatter)
    streamhandler.setLevel(log_level)
    logger.addHandler(streamhandler)


def _http_url_type(url):
    regex = re.compile(
        r'^(?:http)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not re.match(regex, url):
        msg = '"{}" is not a valid URL'.format(url)
        raise argparse.ArgumentTypeError(msg)

    return url


def _build_url_from_host(host, proto, port):
    port_map = {
        'http': 80,
        'https': 443
    }

    port = port if port else port_map.get(proto, 443)

    url = '{proto}://{host}:{port}'.format(
        proto=proto,
        host=host,
        port=port
    )

    try:
        url = _http_url_type(url)
    except argparse.ArgumentTypeError as e:
        logger.error(e)
        sys.exit(1)

    return _http_url_type(url)


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Get Cookie from the session and pass to openconnect.'
    )
    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    parser_host = subparsers.add_parser(
        'host',
        help='use "host" if the endpoint is hosted at the root of the address'
    )
    parser_host.add_argument(
        'host',
        type=str,
        help='The host which serves the VPN.'
    )
    parser_host.add_argument(
        '-pr',
        '--proto',
        type=str,
        default='https',
        help='either http or https -- defaults to https'
    )
    parser_host.add_argument(
        '-po',
        '--port',
        type=int,
        # default=443,
        help='the port to be used -- defaults to 443'
    )

    parser_url = subparsers.add_parser(
        'url',
        help='use "url" if you want to use a specific url (helps if the endpoint is hosted at a sub-path)'
    )
    parser_url.add_argument(
        'url',
        type=_http_url_type,
        help='The URL-Endpoint which serves the landing page.'
    )

    parser.add_argument(
        '-b',
        '--binary',
        type=str,
        default='',
        help='nome of the binary - eg "google-chrome-stable"'
    )

    parser.add_argument(
        '-c',
        '--cookie',
        type=str,
        default='DSID',
        help='name of the cookie to fetch - defaults to DSID'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='-v loglevel INFO, -vv loglevel DEBUG'
    )

    return parser.parse_known_args()


def main():
    args, unknown_args = _parse_args()
    log_map = {
        0: 'WARNING',
        1: 'INFO',
        2: 'DEBUG'
    }
    loglevel = log_map.get(args.verbose, 'DEBUG')
    prepare_logger(loglevel)
    url = args.url if hasattr(args, 'url') else _build_url_from_host(
        args.host,
        args.proto,
        args.port
    )

    driver = ChromeSession(
        url=url,
        cookie_name=args.cookie
    )

    loop = asyncio.get_event_loop()

    cookie = '='.join(driver.loop_wait_cookie())

    # workaround to fix too fast closing of the browser
    # it sometimes led to incomplete cookies
    loop.create_task(driver.wait_cookie_sync(5))

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda: loop.create_task(stop_vpn(s, loop))
        )

    try:
        loop.create_task(run_openconnect(url, cookie, args.verbose, unknown_args))
        loop.run_forever()
    finally:
        loop.close()
        sys.exit()


if __name__ == '__main__':
    main()
