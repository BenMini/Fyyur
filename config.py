import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgres:///benminifie@localhost:5432/fyyur'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
