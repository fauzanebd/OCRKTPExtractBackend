from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import auth, data, helper
    app.register_blueprint(helper.bp)

    app.register_blueprint(auth.bp)
    auth.bp.app_config = app.config
    
    app.register_blueprint(data.bp)
    data.bp.app_config = app.config

    return app