from flask import Blueprint, render_template, request, redirect, url_for
# Pastikan nama fungsinya adalah run_analysis
from app.ml_engine.pipeline import run_analysis

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/models')
def models():
    return render_template('models.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

# Rute Analysis yang sudah menangkap 6 input (termasuk Type mesin)
@main_bp.route('/analysis', methods=['GET', 'POST'])
def analysis():
    if request.method == 'POST':
        # 1. Menangkap semua data dari form HTML
        input_data = {
            # Tambahkan tangkapan untuk tipe mesin (L/M/H)
            "Type": request.form.get('machine_type', 'L'),
            "Air temperature [K]": float(request.form.get('air_temperature', 0)),
            "Process temperature [K]": float(request.form.get('process_temperature', 0)),
            "Rotational speed [rpm]": float(request.form.get('rotational_speed', 0)),
            "Torque [Nm]": float(request.form.get('torque', 0)),
            "Tool wear [min]": float(request.form.get('tool_wear', 0))
        }
        
        # 2. Mengirim data ke pipeline ML (K-Means & Random Forest)
        hasil_prediksi = run_analysis(input_data)
        
        # 3. Melemparkan hasil prediksi ke halaman result.html
        return render_template('result.html', hasil=hasil_prediksi, data_sensor=input_data)

    # Jika GET, tampilkan halaman form
    return render_template('analysis.html')