from __future__ import print_function

import re
from distutils.version import LooseVersion
from urlparse import urljoin

import requests
from bs4 import BeautifulSoup
from flask import current_app as app

from dict8or.app import celery, redis
from dict8or.tasks.util import _fetch_and_extract


RE_FILE_VERSION = re.compile(r'(.*)-(?P<version>.*).tar.gz')


def extract_version(file_name):
    m = re.match(RE_FILE_VERSION, file_name)
    if m:
        return LooseVersion(m.group('version'))


@celery.task
def fetch_and_check(pkg_name):
    # get PyPI tarball page
    url = app.config['PYPI_LIST_URL'] + pkg_name + '/'
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content)

        # order tarballs by version
        tarballs = dict((l.get_text(), l.get('href')) for l in soup.find_all('a')
                        if l.get_text().endswith('.tar.gz'))
        choice = sorted(tarballs.iteritems(), key=lambda e: extract_version(e[0]))[-1]

        print(_fetch_and_extract(pkg_name, choice[0], urljoin(url, choice[1])))

        pep8_check()
        redis.srem('pending_packages', pkg_name.lower())
    else:
        print("Error getting '{} ({})'".format(url, r.status_code))


@celery.task
def fetch_pypi_list():
    url = app.config['PYPI_LIST_URL']

    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content)

        packages = dict((l.get_text(), l.get('href')) for l in soup.find_all('a'))
        print("Packages retrieved")

        # save result to DB
        redis.delete('pypi_packages')
        redis.hmset('pypi_packages', packages)
        print("Saved in DB")

    else:
        print("Impossible to fetch PyPI list: {}: {}".format(r.status_code, r.content))


@celery.task
def add_package(pkg_name):
    with storage() as db:
        if db.sismember('pending_packages', pkg_name) is None:
            if db.hexists('pypi_packages', pkg_name):
                db.sadd('pending_packages', pkg_name)
                fetch_and_check(pkg_name)
                db.srem('pending_packages', pkg_name)
            else:
                print("Package {} doesn't exist!".format(pkg_name))
        else:
            # package already added, ignore
            print("Package {} is already being processed.".format(pkg_name))
            return
