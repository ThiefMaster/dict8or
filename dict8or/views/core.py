from collections import OrderedDict
from itertools import izip

from flask import Blueprint, render_template
from dict8or.app import redis


core = Blueprint('core', __name__)


@core.route('/')
def index():
    ranking = _fetch_ranking()
    return render_template('index.html', ranking=ranking)


def _fetch_ranking():
    ranking = OrderedDict()
    keys = 'warnings', 'errors'
    for p in redis.zrangebyscore('ranking', '-inf', 'inf'):
        ranking[p] = dict(izip(keys, redis.hmget('pkg:' + p, keys)))
    return ranking
