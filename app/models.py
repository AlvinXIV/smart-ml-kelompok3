from datetime import datetime

<<<<<<< Updated upstream
# Schema placeholder for database models (User, MachineAnalysis)
class User:
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

class MachineAnalysis:
    def __init__(self, id, machine_type, air_temp, process_temp, rotational_speed, torque, tool_wear,
                 failure_pred, failure_prob, cluster, condition, action, q_value, created_at=None):
        self.id = id
        self.machine_type = machine_type
        self.air_temp = air_temp
        self.process_temp = process_temp
        self.rotational_speed = rotational_speed
        self.torque = torque
        self.tool_wear = tool_wear
        self.failure_pred = failure_pred
        self.failure_prob = failure_prob
        self.cluster = cluster
        self.condition = condition
        self.action = action
        self.q_value = q_value
        self.created_at = created_at or datetime.now()
=======

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
>>>>>>> Stashed changes
