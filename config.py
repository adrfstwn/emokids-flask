import os

class Config:
    FLASK_APP = os.environ.get('FLASK_APP')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ASSETS_ROOT = os.environ.get('ASSET_ROOT') or 'static/assets'
    FLASK_ENV = os.environ.get('FLASK_ENV')
    TWILIO_ACCOUNT_SID = 'ACea64d8b51d0158316ff2865393d52309'
    TWILIO_AUTH_TOKEN = '4f1aed902552d02bd0ac212598a17177'
    TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'
    USER_WHATSAPP_NUMBER = 'whatsapp:+6281227514494'
