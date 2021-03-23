import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = os.environ.get('DEBUG')
POSTGRE_HOST = '127.0.0.1'
POSTGRE_PORT = '5432'
POSTGRE_USER = os.environ.get('POSTGRE_USER')
POSTGRE_PASSWORD = os.environ.get('POSTGRE_PASSWORD')
POSTGRE_DATABASE = 'flask_hw'
POSTGRE_DSN = f'postgres://{POSTGRE_USER}:{POSTGRE_PASSWORD}@{POSTGRE_HOST}:{POSTGRE_PORT}/{POSTGRE_DATABASE}'