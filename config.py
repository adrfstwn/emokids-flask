import os

class Config:
    FLASK_APP = os.environ.get('FLASK_APP')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ASSETS_ROOT = os.environ.get('ASSET_ROOT') or 'static/assets'
    FLASK_ENV = os.environ.get('FLASK_ENV')
