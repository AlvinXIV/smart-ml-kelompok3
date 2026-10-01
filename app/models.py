from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

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

    def __init__(self, username=None, email=None, password_hash=None, **kwargs):
        super().__init__(**kwargs)
        if username:
            self.username = username
        if email:
            self.email = email
        if password_hash:
            self.password_hash = password_hash

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

    def __init__(self, user_id=None, machine_type=None, air_temp=None, process_temp=None,
                 rotational_speed=None, torque=None, tool_wear=None, failure_pred=None,
                 failure_prob=None, cluster=None, condition=None, action=None, q_value=None,
                 created_at=None, **kwargs):
        super().__init__(**kwargs)
        if user_id is not None:
            self.user_id = user_id
        if machine_type is not None:
            self.machine_type = machine_type
        if air_temp is not None:
            self.air_temp = air_temp
        if process_temp is not None:
            self.process_temp = process_temp
        if rotational_speed is not None:
            self.rotational_speed = rotational_speed
        if torque is not None:
            self.torque = torque
        if tool_wear is not None:
            self.tool_wear = tool_wear
        if failure_pred is not None:
            self.failure_pred = failure_pred
        if failure_prob is not None:
            self.failure_prob = failure_prob
        if cluster is not None:
            self.cluster = cluster
        if condition is not None:
            self.condition = condition
        if action is not None:
            self.action = action
        if q_value is not None:
            self.q_value = q_value
        if created_at is not None:
            self.created_at = created_at
