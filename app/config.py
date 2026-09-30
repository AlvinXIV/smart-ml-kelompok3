import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-predictive-maintenance-2026')
    
    # URL Database (PostgreSQL Only)
    # Jika berjalan di dalam Docker, akan menggunakan DATABASE_URL dari docker-compose.
    # Jika dijalankan lokal (python run.py), akan menembak port 5432 di localhost (meneruskan ke container).
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'postgresql://admin:secretpassword@localhost:5432/ai_maintenance'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False