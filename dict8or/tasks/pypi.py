import re

import celery
import requests
import redis

from dict8or.app import make_app


RE_PYPI_LIST_ENTRY = re.compile(r'<a href=[\'"](.*)[\'"]>([^<]+)</a>')

@celery.task
def fetch_pypi_list():
    app = make_app()
    db = redis.Redis.from_url(app.config['DB_STORAGE'])

    url = app.config['PYPI_LIST_URL']

    r = requests.get(url)
    if r.status_code == 200:
        list_packages = dict((e[1], url + e[0]) for e in re.findall(RE_PYPI_LIST_ENTRY, r.content))
    else:
        print("Impossible to fetch PyPI list: {}: {}".format(r.status_code, r.content))

    print("Packages retrieved")

    db.delete('PYPI_PACKAGES')
    db.hmset('PYPI_PACKAGES', list_packages)
    print("Saved in DB")
