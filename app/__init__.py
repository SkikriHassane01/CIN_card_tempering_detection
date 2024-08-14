from flask import Flask
from config import Config,DevelopmentConfig,ProductionConfig

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    from app import routes
    app.register_blueprint(routes.bp)

    return app