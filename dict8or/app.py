from flask import Flask
from webassets import Environment, Bundle

from dict8or.util import CSSPrefixer
from dict8or.views.core import core


def setup_assets(app):
    assets = Environment(app)  # environment is needed for webassets cli build
    assets.debug = app.debug
    js = Bundle('js/lib/jquery.js',
                filters='rjsmin', output='assets/bundle.%(version)s.js')
    css = Bundle('css/reset.css', 'css/jquery-ui.css',
                 filters=('less', 'cssrewrite', CSSPrefixer(), 'cssmin'), output='assets/bundle.%(version)s.css')
    assets.register('js_all', js)
    assets.register('css_all', css)


def make_app():
    app = Flask('dict8or')
    app.config.from_pyfile('config.py')
    setup_assets(app)
    app.register_blueprint(core)
    return app