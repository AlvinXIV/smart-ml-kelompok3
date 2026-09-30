import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-predictive-maintenance-2026')
    
    # Tambahkan +psycopg2 agar SQLAlchemy menggunakan driver yang tepat
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'postgresql+psycopg2://admin:secretpassword@localhost:5432/ai_maintenance'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False