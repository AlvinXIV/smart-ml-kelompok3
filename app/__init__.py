from flask import Flask
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

    # Import dan daftarkan semua blueprint
    from app.routes.main import main_bp
    from app.routes.analysis import analysis_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(auth_bp)

    return app