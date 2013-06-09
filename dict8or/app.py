import os
from flask import Flask
from flask.ext.assets import Environment, Bundle
from glob import glob

from dict8or.views.core import core


def setup_assets(app):
    assets = Environment(app)
    assets.debug = app.debug
    static_base = os.path.join(app.root_path, 'static')
    bootstrap_files = [os.path.relpath(path, static_base) for path in
                       glob(os.path.join(static_base, 'js/lib/bootstrap-*.js'))]
    bootstrap = Bundle(*bootstrap_files)
    js = Bundle('js/lib/jquery-2.0.2.js', bootstrap, 'js/dict8or.js',
                filters='rjsmin', output='assets/bundle.%(version)s.js')
    css = Bundle('less/lib/bootstrap.less', 'less/core.less',
                 filters=('less', 'cssrewrite', 'cssmin'), output='assets/bundle.%(version)s.css')
    assets.register('js_all', js)
    assets.register('css_all', css)


def make_app():
    app = Flask('dict8or')
    app.config.from_pyfile('config.py')
    setup_assets(app)
    app.register_blueprint(core)
    return app