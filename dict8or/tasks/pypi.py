from __future__ import print_function

import re
import os
import shutil

import requests
from bs4 import BeautifulSoup
from flask import current_app as app
from pip.req import InstallRequirement
from pip.index import PackageFinder

from dict8or.app import celery, redis
from dict8or.tasks.util import _fetch_and_extract
from dict8or.tasks.pep8check import pep8_check

RE_FILE_VERSION = re.compile(r'(.*)-(?P<version>.*).tar.gz')


@celery.task
def fetch_and_check(pkg_name):
    # get PyPI tarball page
    pf = PackageFinder([], [app.config['PYPI_LIST_URL']])

    link = pf.find_requirement(InstallRequirement.from_line(pkg_name, None), False)
    dir_path = _fetch_and_extract(pkg_name, link.filename, link.url)
    try:
        pep8_check(pkg_name, os.path.join(dir_path, '.'.join(link.filename.split('.')[:-2])))
    finally:
        # remove tmp
        shutil.rmtree(dir_path, ignore_errors=True)
        redis.srem('pending_packages', pkg_name.lower())


@celery.task
def fetch_pypi_list():
    url = app.config['PYPI_LIST_URL']

    print("Fetching packages")

    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content)

        packages = (link.get_text() for link in soup.find_all('a'))
        print("Packages retrieved")

        # save result to DB
        with redis.pipeline() as pipe:
            pipe.delete('pypi_packages')
            pipe.sadd('pypi_packages', *packages)
            pipe.execute()
        print("Saved in DB")

    else:
        print("Impossible to fetch PyPI list: {}: {}".format(r.status_code, r.content))


@celery.task
def update_result(pkg_name):
    fetch_and_check(pkg_name)


@celery.task
def update_results():
    for pkg_name in redis.hvals('ranking'):
        update_result(pkg_name).delay()
