from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    print(app.config['SQLALCHEMY_DATABASE_URI'])

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import auth, data, helper, user, locations, visi_misi, dpt, candidate_profile
    app.register_blueprint(helper.bp)

    app.register_blueprint(auth.bp)
    auth.bp.app_config = app.config
    
    app.register_blueprint(data.bp)
    data.bp.app_config = app.config
    
    app.register_blueprint(user.bp)
    user.bp.app_config = app.config
    
    app.register_blueprint(locations.bp)
    locations.bp.app_config = app.config
    
    app.register_blueprint(visi_misi.bp)
    visi_misi.bp.app_config = app.config
    
    app.register_blueprint(dpt.bp)
    dpt.bp.app_config = app.config
    
    app.register_blueprint(candidate_profile.bp)
    candidate_profile.bp.app_config = app.config

    return app