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
        values = [v.decode('utf-8') for v in redis.hmget(p, 'warnings', 'errors')]
        ranking[p] = {"warnings": values[0], "errors": values[1]}
    return ranking
