from flask import Flask
from flask.ext.assets import Environment, Bundle

from dict8or.util import CSSPrefixer
from dict8or.views.core import core


def setup_assets(app):
    assets = Environment(app)  # environment is needed for webassets cli build
    assets.debug = app.debug
    js = Bundle('js/lib/jquery-2.0.2.js', 'js/lib/bootstrap-button.js',
                filters='rjsmin', output='assets/bundle.%(version)s.js')
    css = Bundle('less/lib/bootstrap.less', 'less/core.less',
                 filters=('less', 'cssrewrite', CSSPrefixer(), 'cssmin'), output='assets/bundle.%(version)s.css')
    assets.register('js_all', js)
    assets.register('css_all', css)


def make_app():
    app = Flask('dict8or')
    app.config.from_pyfile('config.py')
    setup_assets(app)
    app.register_blueprint(core)
    return app