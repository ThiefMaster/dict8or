import os
from glob import glob

from celery import Celery
from flask import Flask, url_for, current_app
from flask.ext.assets import Environment, Bundle
from redis import StrictRedis
from werkzeug.local import LocalProxy


def setup_assets(app):
    assets = Environment(app)
    assets.debug = app.debug
    static_base = os.path.join(app.root_path, 'static')
    bootstrap_files = [os.path.relpath(path, static_base) for path in
                       glob(os.path.join(static_base, 'js/lib/bootstrap-*.js'))]
    bootstrap = Bundle(*bootstrap_files)
    js = Bundle('js/lib/jquery-2.0.2.js', 'js/lib/underscore.js', bootstrap, 'js/dict8or.js',
                filters='rjsmin', output='assets/bundle.%(version)s.js')
    css = Bundle('less/lib/bootstrap.less', 'less/core.less',
                 filters=('less', 'cssrewrite', 'cssmin'), output='assets/bundle.%(version)s.css')
    assets.register('js_all', js)
    assets.register('css_all', css)


def setup_jinja(app):
    @app.context_processor
    def _context_processor():
        return {
            'js_api_urls': {
                'search_pypi_packages': url_for('api.search_pypi_packages'),
                'enqueue_pypi_package': url_for('api.enqueue_pypi_package')
            }
        }


def setup_blueprints(app):
    from dict8or.views.core import core
    from dict8or.views.api import api
    app.register_blueprint(core)
    app.register_blueprint(api)


def make_celery():
    celery = Celery()
    celery.config_from_object('celeryconfig')
    return celery


def make_app():
    app = Flask('dict8or')
    app.config.from_pyfile('config.py')
    setup_assets(app)
    setup_jinja(app)
    setup_blueprints(app)
    return app


def _get_redis():
    if not hasattr(current_app, '_redis'):
        current_app._redis = StrictRedis.from_url(current_app.config['DB_STORAGE'], decode_responses=True)
    return current_app._redis


celery = make_celery()
redis = LocalProxy(_get_redis)