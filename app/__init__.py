from flask import Flask
from app.config import Config
from app.models import db

def create_app():
    app = Flask(__name__)
    
    # Load konfigurasi database
    app.config.from_object(Config)

    # Inisialisasi database
    db.init_app(app)

    # Buat tabel otomatis
    with app.app_context():
        db.create_all()

    # Import dan daftarkan blueprint
    from app.routes.main import main_bp
    from app.routes.analysis import analysis_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)

    return app