from datetime import datetime

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
