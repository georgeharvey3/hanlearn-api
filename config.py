import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'learnzhongwen'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'hanlearn_dev.db')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

config = {
    'dev': Config
}