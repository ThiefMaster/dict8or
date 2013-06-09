from collections import OrderedDict

from flask import Blueprint, render_template
from dict8or.app import redis


core = Blueprint('core', __name__)


@core.route('/')
def index():
    ranking = _fetch_ranking()
    return render_template('index.html', ranking=ranking)


def _fetch_ranking():
    ranking = OrderedDict()
    packages = [p.decode('utf-8') for p in redis.zrangebyscore('ranking', '-inf', 'inf')]
    for p in packages:
        ranking[p] = {k.decode('utf-8'): v.decode('utf-8') for (k, v) in redis.hgetall(p).iteritems()}
    return ranking
