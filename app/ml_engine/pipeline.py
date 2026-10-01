import os
import joblib
import pandas as pd

# 1. Setup Path Direktori Model
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'saved_models')

# (Unsupervised - K-Means)
scaler_kmeans = joblib.load(os.path.join(MODELS_DIR, 'scaler.pkl'))
km_loaded = joblib.load(os.path.join(MODELS_DIR, 'kmeans_model.pkl'))
kmeans_model = km_loaded['model'] if isinstance(km_loaded, dict) else km_loaded

# (Supervised - Random Forest)
preprocessor_clf = joblib.load(os.path.join(MODELS_DIR, 'preprocessor_clf.pkl'))
rf_loaded = joblib.load(os.path.join(MODELS_DIR, 'random_forest_model.pkl'))
rf_model = rf_loaded['model'] if isinstance(rf_loaded, dict) else rf_loaded

def run_analysis(input_data):
    """
    Fungsi ini menerima dictionary input_data dari web, misalnya:
    {'Type': 'L', 'Air temperature [K]': 298.1, ...}
    """
    
    # ==========================================
    # A. PREDIKSI RANDOM FOREST (Machine Failure)
    # ==========================================
    features_clf = [
        "Type",
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]"
    ]
    df_clf = pd.DataFrame([input_data], columns=features_clf)
    
    # Eksekusi preprocessor (OneHotEncoding & Scaling) lalu prediksi
    processed_clf_data = preprocessor_clf.transform(df_clf)
    failure_pred = int(rf_model.predict(processed_clf_data)[0])
    
    # Hitung probabilitas kegagalan riil dari Random Forest
    if hasattr(rf_model, "predict_proba"):
        probs = rf_model.predict_proba(processed_clf_data)[0]
        failure_prob = round(float(probs[1]) * 100, 2)
    else:
        failure_prob = 85.0 if failure_pred == 1 else 5.0
    
    # ==========================================
    # B. PREDIKSI K-MEANS (Performa Mesin)
    # ==========================================
    # K-Means di notebook Anda tidak memakai kolom 'Type'
    features_kmeans = [
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]"
    ]
    df_kmeans = pd.DataFrame([input_data], columns=features_kmeans)
    
    # Eksekusi scaler lalu tentukan cluster
    scaled_kmeans_data = scaler_kmeans.transform(df_kmeans)
    cluster_id = int(kmeans_model.predict(scaled_kmeans_data)[0])
    
    # ==========================================
    # C. FORMATTING HASIL MACHINE LEARNING
    # ==========================================
    cluster_labels = {
        0: "Suhu Operasi Tinggi",
        1: "Kondisi Operasi Optimal",
        2: "Putaran Tinggi, Torsi Rendah"
    }
    
    health_score = round(max(0.0, min(100.0, 100.0 - failure_prob)), 1)
    
    return {
        "failure_status": "Risiko Kegagalan Terdeteksi" if failure_pred == 1 else "Kondisi Operasi Normal",
        "failure_code": failure_pred,
        "failure_prob": failure_prob,
        "health_score": health_score,
        "cluster_group": cluster_id,
        "cluster_desc": cluster_labels.get(cluster_id, "Kondisi Operasi Normal")
    }

def predict_machine(machine_type='L', air_temp=298.1, process_temp=308.6, rotational_speed=1551.0, torque=42.8, tool_wear=120.0):
    """
    Wrapper fungsi predict_machine yang menerima argumen individual
    dan mengembalikan dict hasil analisis ensemble Random Forest & K-Means.
    """
    input_data = {
        "Type": machine_type,
        "Air temperature [K]": float(air_temp),
        "Process temperature [K]": float(process_temp),
        "Rotational speed [rpm]": float(rotational_speed),
        "Torque [Nm]": float(torque),
        "Tool wear [min]": float(tool_wear)
    }
    analysis = run_analysis(input_data)
    failure_pred = analysis.get("failure_code", 0)
    failure_prob = analysis.get("failure_prob", 12.4)
    cluster_id = analysis.get("cluster_group", 1)
    
    return {
        'failure_prediction': 'FAILURE RISK' if failure_pred == 1 or failure_prob >= 50.0 else 'NORMAL',
        'failure_probability': failure_prob,
        'cluster': cluster_id,
        'cluster_condition': analysis.get("cluster_desc", "Kondisi Operasi Normal"),
        'health_score': analysis.get("health_score", 87.6),
        'details': analysis
    }