# third-party imports
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_modals import Modal
from flask_marshmallow import Marshmallow
from pathlib import Path

import os
# local imports
from config import app_config
# db variable initialization
db = SQLAlchemy()
ma = Marshmallow()
modal = Modal()

login_manager = LoginManager()

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config.update(
        EBAY_CONFIG_LOC=os.path.join(*Path(__file__).parts[:-2], 'instance\ebay-config.json'),
        IMAGE_UPLOAD_PATH=os.path.join(basedir, 'uploads/images'),
        THUMBNAIL_UPLOAD_PATH=os.path.join(basedir, 'uploads/images/thumbnails'),
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'},
    )

    Bootstrap(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "auth.login"
    migrate = Migrate(app, db)
    from app import models
    
    basedir = os.path.abspath(os.path.dirname(__file__))

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    modal.init_app(app)
    ma.init_app(app)
    
    return app