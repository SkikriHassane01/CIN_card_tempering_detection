""" Flask config."""

from os import environ, path

basedir = path.abspath(path.dirname(__file__))

#general config
class Config(object):
    SECRET_KEY = environ.get('SECRET_KEY')
    UPLOAD_FOLDER = "app/static/uploads"
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    SECTION_COOKIE_SECURE = True
    DEBUG = False
    TESTING = False

# Development config
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    SECTION_COOKIE_SECURE = False

# Production config
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SECTION_COOKIE_SECURE = True
