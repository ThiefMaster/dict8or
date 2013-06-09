from flask import Blueprint, jsonify, request
from dict8or.app import redis


api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/search-pypi-packages')
def search_pypi_packages():
    search = request.args['search'].lower()
    packages = (p.decode('utf-8') for p in redis.hkeys('PYPI_PACKAGES'))
    packages = [p for p in packages if search in p.lower()]
    return jsonify(packages=packages)