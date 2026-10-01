from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Inisialisasi object database
db = SQLAlchemy()

class MachineAnalysis(db.Model):
    __tablename__ = 'analysis_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    
    # Parameter Masukan (Sensor Telemetry)
    machine_type = db.Column(db.String(5), nullable=False)
    air_temp = db.Column(db.Float, nullable=False)
    process_temp = db.Column(db.Float, nullable=False)
    rotational_speed = db.Column(db.Integer, nullable=False)
    torque = db.Column(db.Float, nullable=False)
    tool_wear = db.Column(db.Integer, nullable=False)
    
    # Luaran Machine Learning (Random Forest & K-Means)
    failure_pred = db.Column(db.String(30), nullable=False) 
    failure_prob = db.Column(db.Float, nullable=False)      
    cluster = db.Column(db.Integer, nullable=False)             
    condition = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(20), nullable=True, default='')  
    q_value = db.Column(db.Float, nullable=True, default=0.0)                  
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)