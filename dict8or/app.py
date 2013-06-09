from flask import Flask

from dict8or.views.core import core


def make_app():
    app = Flask('dict8or')
    app.config.from_pyfile('config.py')
    app.register_blueprint(core)
    return app