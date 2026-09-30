from flask import Flask, render_template
from app.config import Config
from app.models import db

def create_app():
    app = Flask(__name__)
    
    # Load konfigurasi dari config.py
    app.config.from_object(Config)

    # Inisialisasi database ke aplikasi Flask
    db.init_app(app)

    # Context ini wajib untuk membuat tabel otomatis di PostgreSQL
    with app.app_context():
        db.create_all()

    # Rute sementara untuk testing
    @app.route('/')
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    return app