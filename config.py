import os
import sqlalchemy.dialects.mysql

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        "mysql+pymysql://ka7617:123456@zanner.org.ua:33321/wolfordb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    POSTS_PER_PAGE = 9