from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time

from config import config

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main.views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .main.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app

