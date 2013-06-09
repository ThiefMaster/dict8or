import re

import celery
import requests
import redis


PYPI_LIST_URL = "https://pypi.python.org/simple/"
RE_PYPI_LIST_ENTRY = re.compile(r'<a href=[\'"](.*)[\'"]>([^<]+)</a>')
DB_STORAGE = 'redis://localhost/0'


@celery.task
def fetch_pypi_list():
    db = redis.Redis.from_url(DB_STORAGE)

    r = requests.get(PYPI_LIST_URL)
    if r.status_code == 200:
        list_packages = dict((e[1], PYPI_LIST_URL + e[0]) for e in re.findall(RE_PYPI_LIST_ENTRY, r.content))
    else:
        print("Impossible to fetch PyPI list: {}: {}".format(r.status_code, r.content))

    print("Packages retrieved")
    db.hmset('PYPI_PACKAGES', list_packages)
    print("Saved in DB")
