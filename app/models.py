from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Inisialisasi object database (Ini yang menyelesaikan error 'db' Anda)
db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relasi one-to-many ke AnalysisHistory
    histories = db.relationship('MachineAnalysis', backref='user', lazy=True)

class MachineAnalysis(db.Model):
    __tablename__ = 'analysis_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Parameter Masukan (Sensor Telemetry)
    machine_type = db.Column(db.String(5), nullable=False)
    air_temp = db.Column(db.Float, nullable=False)
    process_temp = db.Column(db.Float, nullable=False)
    rotational_speed = db.Column(db.Integer, nullable=False)
    torque = db.Column(db.Float, nullable=False)
    tool_wear = db.Column(db.Integer, nullable=False)
    
    # Luaran Machine Learning
    failure_pred = db.Column(db.String(20), nullable=False) 
    failure_prob = db.Column(db.Float, nullable=False)      
    cluster = db.Column(db.Integer, nullable=False)             
    condition = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(20), nullable=False)  
    q_value = db.Column(db.Float, nullable=False)                  
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)