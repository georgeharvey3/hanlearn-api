import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'learnzhongwen'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'hanlearn_dev.db')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

config = {
    'dev': Config
}