import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-predictive-maintenance-2026')
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'app.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
