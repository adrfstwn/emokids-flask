import os

class Config:
    FLASK_APP = 'app.py'
    SECRET_KEY = 'aGVuU2VjdXJlX3NlY3JldF9rZXktQWxvbmdTdHJpbmdUZXh0'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@127.0.0.1:3306/emokids'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ASSETS_ROOT = 'static/assets'
    FLASK_ENV = 'development'
