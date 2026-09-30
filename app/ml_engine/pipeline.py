"""
ML Pipeline combining:
1. Supervised Learning: Random Forest (Failure Risk & Probability)
2. Unsupervised Learning: K-Means (Operating Condition Cluster)
3. Reinforcement Learning: Q-Learning (Maintenance Recommendation Policy)
"""

def predict_machine(machine_type, air_temp, process_temp, rotational_speed, torque, tool_wear):
    """
    Mock inference pipeline for UI and demonstration.
    Returns results adhering to the dataset metrics and UI specifications.
    """
    # Heuristic demonstration logic based on typical AI4I failure indicators (e.g. high torque & high tool wear or high temps)
    risk_score = 0.05
    if float(torque) > 60:
        risk_score += 0.35
    if float(tool_wear) > 180:
        risk_score += 0.40
    temp_diff = float(process_temp) - float(air_temp)
    if temp_diff < 8.6:
        risk_score += 0.15
        
    failure_prob = round(min(max(risk_score, 0.05), 0.95) * 100, 1)
    is_failure = failure_prob > 50.0

    if is_failure:
        failure_pred = "FAILURE RISK"
        cluster = 2
        condition = "High Load Condition"
        action = "MAINTENANCE"
        q_value = 8.92
    elif failure_prob > 25.0 or float(tool_wear) > 100:
        failure_pred = "NORMAL"
        cluster = 1
        condition = "Medium Operating Condition"
        action = "INSPECT"
        q_value = 6.82
    else:
        failure_pred = "NORMAL"
        cluster = 0
        condition = "Optimal Operating Condition"
        action = "CONTINUE"
        q_value = 9.45

    return {
        "failure_prediction": failure_pred,
        "failure_probability": failure_prob,
        "cluster": cluster,
        "cluster_condition": condition,
        "recommended_action": action,
        "q_value": q_value
    }
