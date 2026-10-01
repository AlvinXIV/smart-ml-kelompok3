import re
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, Response
from app.ml_engine.pipeline import predict_machine, analyze_machine
from app.report import build_report_pdf

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analysis', methods=['GET', 'POST'])
def analysis():
    if request.method == 'POST':
        machine_type = request.form.get('machine_type', 'L')
        air_temp = float(request.form.get('air_temp', 298.1))
        process_temp = float(request.form.get('process_temp', 308.6))
        rotational_speed = float(request.form.get('rotational_speed', 1551))
        torque = float(request.form.get('torque', 42.8))
        tool_wear = float(request.form.get('tool_wear', 120))

        result = predict_machine(machine_type, air_temp, process_temp, rotational_speed, torque, tool_wear)
        
        return render_template('result.html',
                               params={
                                   'machine_type': machine_type,
                                   'air_temp': air_temp,
                                   'process_temp': process_temp,
                                   'rotational_speed': rotational_speed,
                                   'torque': torque,
                                   'tool_wear': tool_wear
                               },
                               result=result)

    return render_template('analysis.html')

@analysis_bp.route('/result')
def result():
    # Support query parameter status (normal vs high_risk) for easy UI preview
    status = request.args.get('status', 'normal')
    if status == 'high_risk':
        params = {
            'machine_type': 'M',
            'air_temp': 301.2,
            'process_temp': 310.8,
            'rotational_speed': 1320,
            'torque': 68.5,
            'tool_wear': 210
        }
        res = {
            'failure_prediction': 'FAILURE RISK',
            'failure_probability': 78.2,
            'cluster': 2,
            'cluster_condition': 'High Load Condition',
            'recommended_action': 'MAINTENANCE',
            'q_value': 8.92
        }
    else:
        params = {
            'machine_type': 'L',
            'air_temp': 298.1,
            'process_temp': 308.6,
            'rotational_speed': 1551,
            'torque': 42.8,
            'tool_wear': 120
        }
        res = {
            'failure_prediction': 'NORMAL',
            'failure_probability': 12.4,
            'cluster': 1,
            'cluster_condition': 'Medium Operating Condition',
            'recommended_action': 'INSPECT',
            'q_value': 6.82
        }
    return render_template('result.html', params=params, result=res)

@analysis_bp.route('/history')
def history():
    # Sample realistic historical records based on prompt section 20 & 35
    history_records = [
        {
            'id': 'AN-9024',
            'date': '2026-09-30 09:42',
            'machine_type': 'L',
            'air_temp': 298.1,
            'process_temp': 308.6,
            'rotational_speed': 1551,
            'torque': 42.8,
            'tool_wear': 120,
            'failure_pred': 'Normal',
            'failure_prob': 12.4,
            'cluster': 1,
            'cluster_condition': 'Medium Operating Condition',
            'action': 'Inspect',
            'q_value': 6.82
        },
        {
            'id': 'AN-9023',
            'date': '2026-09-30 08:15',
            'machine_type': 'M',
            'air_temp': 301.5,
            'process_temp': 311.2,
            'rotational_speed': 1310,
            'torque': 69.4,
            'tool_wear': 215,
            'failure_pred': 'High Risk',
            'failure_prob': 78.2,
            'cluster': 2,
            'cluster_condition': 'High Load Condition',
            'action': 'Maintenance',
            'q_value': 8.92
        },
        {
            'id': 'AN-9022',
            'date': '2026-09-29 16:30',
            'machine_type': 'H',
            'air_temp': 297.8,
            'process_temp': 308.1,
            'rotational_speed': 1580,
            'torque': 38.2,
            'tool_wear': 45,
            'failure_pred': 'Normal',
            'failure_prob': 8.7,
            'cluster': 0,
            'cluster_condition': 'Optimal Operating Condition',
            'action': 'Continue',
            'q_value': 9.45
        },
        {
            'id': 'AN-9021',
            'date': '2026-09-29 11:20',
            'machine_type': 'L',
            'air_temp': 298.4,
            'process_temp': 308.9,
            'rotational_speed': 1490,
            'torque': 44.5,
            'tool_wear': 95,
            'failure_pred': 'Normal',
            'failure_prob': 14.1,
            'cluster': 1,
            'cluster_condition': 'Medium Operating Condition',
            'action': 'Inspect',
            'q_value': 6.75
        },
        {
            'id': 'AN-9020',
            'date': '2026-09-28 14:05',
            'machine_type': 'H',
            'air_temp': 297.5,
            'process_temp': 307.9,
            'rotational_speed': 1610,
            'torque': 36.1,
            'tool_wear': 18,
            'failure_pred': 'Normal',
            'failure_prob': 5.2,
            'cluster': 0,
            'cluster_condition': 'Optimal Operating Condition',
            'action': 'Continue',
            'q_value': 9.60
        },
        {
            'id': 'AN-9019',
            'date': '2026-09-28 09:12',
            'machine_type': 'M',
            'air_temp': 302.1,
            'process_temp': 311.8,
            'rotational_speed': 1280,
            'torque': 72.8,
            'tool_wear': 230,
            'failure_pred': 'High Risk',
            'failure_prob': 84.6,
            'cluster': 2,
            'cluster_condition': 'High Load Condition',
            'action': 'Maintenance',
            'q_value': 9.10
        }
    ]
    return render_template('history.html', records=history_records)


# ----------------------------------------------------------------------
# API analisis lengkap + ekspor laporan PDF (dipakai halaman Machine Analysis)
# ----------------------------------------------------------------------
_BOUNDS = {
    'air_temp': (250, 350), 'process_temp': (250, 350),
    'rotational_speed': (0, 10000), 'torque': (0, 500), 'tool_wear': (0, 1000),
}


def _parse_inputs(src):
    """Validasi input dari JSON/form. Mengembalikan (dict, error)."""
    mtype = str(src.get('machine_type', 'L')).upper()
    if mtype not in ('L', 'M', 'H'):
        return None, 'machine_type harus L, M, atau H'
    out = {'machine_type': mtype}
    for key, (lo, hi) in _BOUNDS.items():
        try:
            val = float(src.get(key))
        except (TypeError, ValueError):
            return None, f'{key} harus berupa angka'
        if not (lo <= val <= hi):
            return None, f'{key} harus di antara {lo} dan {hi}'
        out[key] = val
    return out, None


@analysis_bp.route('/api/analyze', methods=['POST'])
def api_analyze():
    inputs, err = _parse_inputs(request.get_json(silent=True) or {})
    if err:
        return jsonify({'error': err}), 400
    return jsonify(analyze_machine(**inputs))


@analysis_bp.route('/analysis/report.pdf', methods=['POST'])
def report_pdf():
    # Hasil dihitung ulang di server dari input agar laporan tidak bergantung data dari browser
    inputs, err = _parse_inputs(request.form)
    if err:
        return jsonify({'error': err}), 400
    result = analyze_machine(**inputs)
    meta = {k: (request.form.get(k) or '')[:80] for k in ('machine_id', 'company', 'prepared_by')}
    pdf = build_report_pdf(result, meta)
    label = re.sub(r'[^A-Za-z0-9_-]+', '-', meta['machine_id']).strip('-') or 'Mesin'
    filename = f"Laporan-Diagnostik-{label}-{result['report_id'][3:]}.pdf"
    return Response(pdf, mimetype='application/pdf',
                    headers={'Content-Disposition': f'attachment; filename="{filename}"'})