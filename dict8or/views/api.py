from flask import Blueprint, jsonify, request
from dict8or.app import redis
from dict8or.tasks.pypi import fetch_and_check


api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/search-pypi-packages')
def search_pypi_packages():
    search = request.args['search'].lower()
    packages = (p.decode('utf-8') for p in redis.hkeys('pypi_packages'))
    packages = [p for p in packages if search in p.lower()]
    return jsonify(packages=packages)


@api.route('/enqueue-pypi-package', methods=('POST',))
def enqueue_pypi_package():
    name = request.form['package']
    if redis.sismember('pending_packages', name.lower()):
        return jsonify(success=False, msg=u'Package is already queued for checking')
    elif not redis.hexists('pypi_packages', name):
        return jsonify(success=False, msg=u'Package does not exist')
    redis.sadd('pending_packages', name.lower())
    fetch_and_check.delay(name)
    return jsonify(success=True)
