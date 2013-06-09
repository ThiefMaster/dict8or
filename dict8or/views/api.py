from flask import Blueprint, jsonify, request

from dict8or.app import redis
from dict8or.tasks.pypi import fetch_and_check


api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/search-pypi-packages')
def search_pypi_packages():
    search = request.args['search'].lower()
    packages = sorted([p for p in redis.smembers('pypi_packages') if search in p.lower()])
    return jsonify(packages=packages)


@api.route('/enqueue-pypi-package', methods=('POST',))
def enqueue_pypi_package():
    name = request.form['package']
    if not redis.sismember('pypi_packages', name):
        return jsonify(success=False, msg=u'Package does not exist')
    if _package_is_queued(name):
        return jsonify(success=False, msg=u'Package is already queued for checking')
    fetch_and_check.delay(name)
    return jsonify(success=True)


def _package_is_queued(package):
    def _helper(pipe):
        if pipe.sismember('pending_packages', package.lower()):
            return True
        pipe.multi()
        pipe.sadd('pending_packages', package.lower())
        return False

    return redis.transaction(_helper, 'pending_packages', value_from_callable=True)
