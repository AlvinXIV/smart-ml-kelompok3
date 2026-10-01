import os
import joblib
import math
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta

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
    failure_pred = rf_model.predict(processed_clf_data)[0]
    
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
    cluster_id = kmeans_model.predict(scaled_kmeans_data)[0]
    
    # ==========================================
    # C. FORMATTING HASIL
    # ==========================================
    # Label cluster ini bisa disesuaikan dengan hasil analisis EDA Anda
    cluster_labels = {
        0: "Performa Optimal",
        1: "Performa Menengah",
        2: "Risiko Degradasi Tinggi"
    }
    
    return {
        "failure_status": "Machine Failure Terdeteksi" if failure_pred == 1 else "Kondisi Normal",
        "failure_code": int(failure_pred),
        "cluster_group": int(cluster_id),
        "cluster_desc": cluster_labels.get(int(cluster_id), "Unknown")
    }

def predict_machine(machine_type='L', air_temp=298.1, process_temp=308.6, rotational_speed=1551.0, torque=42.8, tool_wear=120.0):
    """
    Wrapper fungsi predict_machine yang menerima argumen individual
    dan mengembalikan dict hasil analisis ensemble.
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
    cluster_id = analysis.get("cluster_group", 1)
    
    return {
        'failure_prediction': 'FAILURE RISK' if failure_pred == 1 else 'NORMAL',
        'failure_probability': 78.2 if failure_pred == 1 else 12.4,
        'cluster': cluster_id,
        'cluster_condition': analysis.get("cluster_desc", "Normal Condition"),
        'recommended_action': 'MAINTENANCE' if failure_pred == 1 else ('INSPECT' if cluster_id == 1 else 'CONTINUE'),
        'q_value': 8.92 if failure_pred == 1 else 6.82,
        'details': analysis
    }


# ======================================================================
# ANALISIS LENGKAP (dipakai halaman Machine Analysis & Laporan Diagnostik)
# Fungsi di atas tidak diubah; bagian ini hanya menambah.
# ======================================================================
FEATURES_CLF = [
    "Type", "Air temperature [K]", "Process temperature [K]",
    "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]",
]
FEATURES_KMEANS = FEATURES_CLF[1:]

# Nama cluster K-Means. Ubah di sini setelah EDA kelompok Anda.
# Catatan: centroid model ini TIDAK dibedakan oleh tool wear (ketiganya ~105-110 menit);
# perbedaannya ada pada suhu serta kombinasi putaran/torsi, jadi nama di bawah mengikuti itu.
CLUSTER_NAMES = {
    0: "Suhu Operasi Tinggi",
    1: "Suhu Operasi Rendah",
    2: "Putaran Tinggi, Torsi Rendah",
}

# Ambang tingkat risiko berdasarkan probabilitas kegagalan (%).
# Batas 50% = batas keputusan kelas bawaan Random Forest.
RISK_MEDIUM_FROM = 25.0
RISK_HIGH_FROM = 50.0

_WIB = timezone(timedelta(hours=7))
_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
          "Agustus", "September", "Oktober", "November", "Desember"]
_CENTROIDS = scaler_kmeans.inverse_transform(kmeans_model.cluster_centers_)


def _fmt_id(x, nd=0):
    """Format angka gaya Indonesia (titik ribuan)."""
    return f"{x:,.{nd}f}".replace(",", ".")


def _global_importance():
    names = preprocessor_clf.get_feature_names_out()
    agg = {}
    for n, v in zip(names, rf_model.feature_importances_):
        key = "Type" if n.startswith("cat__Type") else n.split("__", 1)[1]
        agg[key] = agg.get(key, 0.0) + float(v)
    total = sum(agg.values()) or 1.0
    rows = [{"feature": k, "importance": round(v / total * 100, 1)} for k, v in agg.items()]
    return sorted(rows, key=lambda r: r["importance"], reverse=True)


try:
    _IMPORTANCE = _global_importance()
except Exception:
    _IMPORTANCE = []


def _metric(d, key):
    try:
        return round(float(d["metrics"][key]), 4)
    except Exception:
        return None


def _model_info():
    rf_m = rf_loaded if isinstance(rf_loaded, dict) else {}
    km_m = km_loaded if isinstance(km_loaded, dict) else {}
    return {
        "rf": {
            "name": "Random Forest",
            "accuracy": _metric(rf_m, "Test Accuracy"),
            "auc": _metric(rf_m, "AUC-ROC"),
            "precision": _metric(rf_m, "Precision"),
            "recall": _metric(rf_m, "Recall"),
            "f1": _metric(rf_m, "F1-Score"),
        },
        "km": {
            "name": "K-Means (k=3)",
            "silhouette": _metric(km_m, "silhouette_score"),
            "davies_bouldin": _metric(km_m, "davies_bouldin_index"),
        },
    }


def _failure_rules(mtype, air, proc, rpm, torque, wear):
    """Aturan mode kegagalan sesuai dokumentasi dataset AI4I 2020."""
    power = torque * rpm * 2 * math.pi / 60
    osf_limit = {"L": 11000, "M": 12000, "H": 13000}.get(mtype, 11000)
    return [
        {"code": "HDF", "name": "Heat Dissipation",
         "condition": "Selisih suhu proses-udara < 8,6 K dan putaran < 1.380 rpm",
         "value": f"selisih {proc - air:.1f} K, {_fmt_id(rpm)} rpm",
         "triggered": round(proc - air, 1) < 8.6 and rpm < 1380},
        {"code": "PWF", "name": "Power",
         "condition": "Daya (torsi x kecepatan sudut) < 3.500 W atau > 9.000 W",
         "value": f"{_fmt_id(power)} W",
         "triggered": power < 3500 or power > 9000},
        {"code": "OSF", "name": "Overstrain",
         "condition": f"Tool wear x torsi > {_fmt_id(osf_limit)} min\u00b7Nm (tipe {mtype})",
         "value": f"{_fmt_id(wear * torque)} min\u00b7Nm",
         "triggered": wear * torque > osf_limit},
        {"code": "TWF", "name": "Tool Wear",
         "condition": "Tool wear berada pada rentang 200-240 menit",
         "value": f"{_fmt_id(wear)} menit",
         "triggered": 200 <= wear <= 240},
    ]


def _param_rows(mtype, air, proc, rpm, torque, wear):
    """Penilaian tiap parameter memakai rentang yang sama dengan form Machine Analysis."""
    def st(ok, warn=False):
        return "ok" if ok else ("warn" if warn else "alert")
    type_name = {"L": "L (Light Duty)", "M": "M (Medium Duty)", "H": "H (Heavy Duty)"}.get(mtype, mtype)
    return [
        {"label": "Tipe Mesin", "value": type_name, "ref": "L / M / H", "status": "ok"},
        {"label": "Suhu Udara", "value": f"{air:.1f} K ({air - 273.15:.1f} \u00b0C)",
         "ref": "285-315 K (optimal \u00b1298 K)", "status": st(285 <= air <= 315, True)},
        {"label": "Suhu Proses", "value": f"{proc:.1f} K ({proc - 273.15:.1f} \u00b0C)",
         "ref": "295-325 K (optimal \u00b1308 K)", "status": st(295 <= proc <= 325, True)},
        {"label": "Kecepatan Putar", "value": f"{_fmt_id(rpm)} rpm",
         "ref": "Aman 1.400-1.800 rpm", "status": st(1400 <= rpm <= 1800, True)},
        {"label": "Torsi", "value": f"{torque:.1f} Nm",
         "ref": "Batas < 60 Nm", "status": st(torque <= 60)},
        {"label": "Tool Wear", "value": f"{_fmt_id(wear)} menit ({wear / 200 * 100:.0f}% dari 200)",
         "ref": "Servis 180 menit, kritis 200 menit",
         "status": "ok" if wear < 180 else ("warn" if wear < 200 else "alert")},
    ]


def analyze_machine(machine_type="L", air_temp=298.1, process_temp=308.6,
                    rotational_speed=1551.0, torque=42.8, tool_wear=120.0):
    """Analisis lengkap: probabilitas kegagalan (RF), cluster (K-Means), aturan & rekomendasi."""
    mtype = str(machine_type).upper()
    air, proc, rpm = float(air_temp), float(process_temp), float(rotational_speed)
    tq, wear = float(torque), float(tool_wear)

    row = {"Type": mtype, "Air temperature [K]": air, "Process temperature [K]": proc,
           "Rotational speed [rpm]": rpm, "Torque [Nm]": tq, "Tool wear [min]": wear}

    # --- Supervised: Random Forest ---
    X = preprocessor_clf.transform(pd.DataFrame([row], columns=FEATURES_CLF))
    classes = list(rf_model.classes_)
    prob = float(rf_model.predict_proba(X)[0][classes.index(1)]) * 100 if 1 in classes else 0.0
    pred = int(rf_model.predict(X)[0])
    level = "high" if prob >= RISK_HIGH_FROM else ("medium" if prob >= RISK_MEDIUM_FROM else "low")

    # --- Unsupervised: K-Means ---
    Xk = scaler_kmeans.transform(pd.DataFrame([row], columns=FEATURES_KMEANS))
    cluster = int(kmeans_model.predict(Xk)[0])
    dist = np.linalg.norm(kmeans_model.cluster_centers_ - Xk, axis=1)
    inv = 1.0 / np.maximum(dist, 1e-9)
    share = inv / inv.sum() * 100
    clusters = []
    for i in range(len(dist)):
        c = _CENTROIDS[i]
        clusters.append({
            "id": i,
            "name": CLUSTER_NAMES.get(i, f"Cluster {i}"),
            "distance": round(float(dist[i]), 3),
            "similarity": round(float(share[i]), 1),
            "assigned": i == cluster,
            "profile": (f"Rata-rata: suhu udara {c[0]:.1f} K, suhu proses {c[1]:.1f} K, "
                        f"{_fmt_id(c[2])} rpm, torsi {c[3]:.1f} Nm, tool wear {_fmt_id(c[4])} menit."),
        })

    rules = _failure_rules(mtype, air, proc, rpm, tq, wear)
    triggered = [r for r in rules if r["triggered"]]
    codes = ", ".join(r["code"] for r in triggered)

    # --- Narasi & rekomendasi (berbasis aturan, bukan model) ---
    if level == "high":
        desc = "Probabilitas kegagalan tinggi terdeteksi oleh Random Forest. Disarankan pemeliharaan sebelum operasi dilanjutkan."
        callout = "Probabilitas kegagalan tinggi; jadwalkan penghentian terkontrol untuk pemeliharaan."
        rec_title = "Pemeliharaan Segera"
        rec_text = ("Jadwalkan penghentian terkontrol dan lakukan pemeliharaan sebelum mesin kembali beroperasi penuh. "
                    "Prioritaskan pemeriksaan komponen yang terindikasi pada pemeriksaan aturan mode kegagalan.")
    elif level == "medium":
        desc = "Probabilitas kegagalan meningkat terdeteksi oleh Random Forest. Jadwalkan inspeksi visual dalam 48 jam operasi."
        callout = "Probabilitas kegagalan meningkat; jadwalkan inspeksi dan pantau parameter secara berkala."
        rec_title = "Inspeksi Terjadwal"
        rec_text = ("Lakukan inspeksi visual dan pengecekan parameter pada jadwal terdekat, "
                    "serta tingkatkan frekuensi pemantauan sampai probabilitas kembali turun.")
    else:
        if triggered:
            desc = "Probabilitas model rendah, namun ada indikator aturan mode kegagalan yang perlu diverifikasi."
        else:
            desc = "Sistem beroperasi dalam kondisi termomekanis nominal. Tidak ada anomali terdeteksi."
        callout = "Parameter berada dalam batas operasional historis yang aman."
        rec_title = "Lanjutkan Operasi"
        rec_text = "Mesin dapat melanjutkan operasi normal dengan pemantauan rutin sesuai jadwal pemeliharaan."
    if triggered:
        callout += f" Indikator aturan terpenuhi: {codes}."

    notes = []
    for r in triggered:
        notes.append(f"Aturan {r['code']} ({r['name']}) terpenuhi: {r['value']}. Verifikasi kondisi komponen terkait.")
    if wear >= 200:
        notes.append("Tool wear telah melewati batas kritis 200 menit; ganti pahat.")
    elif wear >= 180:
        notes.append("Tool wear telah melewati batas servis 180 menit; rencanakan penggantian pahat.")
    if torque > 60:
        notes.append("Torsi melebihi batas 60 Nm; periksa beban kerja dan kondisi spindle.")

    now = datetime.now(_WIB)
    return {
        "report_id": "DX-" + now.strftime("%Y%m%d-%H%M%S"),
        "generated_at": f"{now.day} {_BULAN[now.month - 1]} {now.year}, {now:%H:%M} WIB",
        "generated_iso": now.isoformat(),
        "inputs": {"machine_type": mtype, "air_temp": air, "process_temp": proc,
                   "rotational_speed": rpm, "torque": tq, "tool_wear": wear},
        "health_score": round(100 - prob, 1),
        "level": level,
        "description": desc,
        "callout": callout,
        "supervised": {
            "model": "Random Forest",
            "failure_probability": round(prob, 1),
            "predicted_class": pred,
            "decision_threshold": RISK_HIGH_FROM,
            "medium_from": RISK_MEDIUM_FROM,
            "feature_importance": _IMPORTANCE[:6],
        },
        "unsupervised": {
            "model": "K-Means (k=3)",
            "cluster": cluster,
            "cluster_name": CLUSTER_NAMES.get(cluster, f"Cluster {cluster}"),
            "clusters": clusters,
        },
        "parameters": _param_rows(mtype, air, proc, rpm, tq, wear),
        "rules": rules,
        "recommendation": {"title": rec_title, "text": rec_text, "notes": notes},
        "model_info": _model_info(),
    }