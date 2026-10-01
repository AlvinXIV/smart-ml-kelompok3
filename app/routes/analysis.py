from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models import db, MachineAnalysis
from app.ml_engine.pipeline import predict_machine

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analysis', methods=['GET', 'POST'])
def analysis():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json() or {}
            machine_type = str(data.get('machine_type', 'L')).upper()
            try:
                air_temp = float(data.get('air_temp', 298.1))
            except (ValueError, TypeError):
                air_temp = 298.1
            try:
                process_temp = float(data.get('process_temp', 308.6))
            except (ValueError, TypeError):
                process_temp = 308.6
            try:
                rotational_speed = float(data.get('rotational_speed', 1551))
            except (ValueError, TypeError):
                rotational_speed = 1551.0
            try:
                torque = float(data.get('torque', 42.8))
            except (ValueError, TypeError):
                torque = 42.8
            try:
                tool_wear = float(data.get('tool_wear', 120))
            except (ValueError, TypeError):
                tool_wear = 120.0
        else:
            machine_type = str(request.form.get('machine_type', 'L')).upper()
            try:
                air_temp = float(request.form.get('air_temp') or request.form.get('air_temperature', 298.1))
            except (ValueError, TypeError):
                air_temp = 298.1
            try:
                process_temp = float(request.form.get('process_temp') or request.form.get('process_temperature', 308.6))
            except (ValueError, TypeError):
                process_temp = 308.6
            try:
                rotational_speed = float(request.form.get('rotational_speed', 1551))
            except (ValueError, TypeError):
                rotational_speed = 1551.0
            try:
                torque = float(request.form.get('torque', 42.8))
            except (ValueError, TypeError):
                torque = 42.8
            try:
                tool_wear = float(request.form.get('tool_wear', 120))
            except (ValueError, TypeError):
                tool_wear = 120.0

        result = predict_machine(machine_type, air_temp, process_temp, rotational_speed, torque, tool_wear)
        
        # Simpan ke PostgreSQL
        record_id = None
        try:
            new_record = MachineAnalysis(
                machine_type=machine_type,
                air_temp=air_temp,
                process_temp=process_temp,
                rotational_speed=int(rotational_speed),
                torque=torque,
                tool_wear=int(tool_wear),
                failure_pred=result.get('failure_prediction', 'Normal'),
                failure_prob=float(result.get('failure_probability', 12.4)),
                cluster=int(result.get('cluster', 1)),
                condition=result.get('cluster_condition', 'Kondisi Operasi Optimal')
            )
            db.session.add(new_record)
            db.session.commit()
            record_id = new_record.id
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error saving to DB: {e}")
            db.session.rollback()

        if request.is_json:
            return jsonify({
                'success': True,
                'record_id': record_id,
                'result': result,
                'params': {
                    'machine_type': machine_type,
                    'air_temp': air_temp,
                    'process_temp': process_temp,
                    'rotational_speed': rotational_speed,
                    'torque': torque,
                    'tool_wear': tool_wear
                }
            })
        
        return render_template('result.html',
                               params={
                                   'machine_type': machine_type,
                                   'air_temp': air_temp,
                                   'process_temp': process_temp,
                                   'rotational_speed': rotational_speed,
                                   'torque': torque,
                                   'tool_wear': tool_wear
                               },
                               result=result,
                               record_id=record_id)

    return render_template('analysis.html')

@analysis_bp.route('/result')
def result():
    # Cek jika ada ID record dari database
    record_id = request.args.get('id')
    if record_id:
        try:
            r = MachineAnalysis.query.get(int(record_id))
            if r:
                params = {
                    'machine_type': r.machine_type,
                    'air_temp': r.air_temp,
                    'process_temp': r.process_temp,
                    'rotational_speed': r.rotational_speed,
                    'torque': r.torque,
                    'tool_wear': r.tool_wear
                }
                res = {
                    'failure_prediction': r.failure_pred,
                    'failure_probability': r.failure_prob,
                    'cluster': r.cluster,
                    'cluster_condition': r.condition,
                    'health_score': round(max(0.0, min(100.0, 100.0 - r.failure_prob)), 1)
                }
                return render_template('result.html', params=params, result=res, record_id=r.id)
        except Exception as e:
            print(f"Error fetching record {record_id}: {e}")

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
            'cluster_condition': 'Putaran Tinggi, Torsi Rendah',
            'health_score': 21.8
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
            'cluster_condition': 'Kondisi Operasi Optimal',
            'health_score': 87.6
        }
    return render_template('result.html', params=params, result=res, record_id=None)

@analysis_bp.route('/history')
def history():
    history_records = []
    try:
        db_records = MachineAnalysis.query.order_by(MachineAnalysis.created_at.desc()).all()
        if db_records:
            history_records = [
                {
                    'id': f"M-{r.id:04d}",
                    'raw_id': r.id,
                    'date': r.created_at.strftime('%d %b, %H:%M') if r.created_at else 'Baru saja',
                    'machine_type': r.machine_type,
                    'air_temp': r.air_temp,
                    'process_temp': r.process_temp,
                    'rotational_speed': r.rotational_speed,
                    'torque': r.torque,
                    'tool_wear': r.tool_wear,
                    'failure_pred': r.failure_pred,
                    'failure_prob': r.failure_prob,
                    'cluster': r.cluster,
                    'cluster_condition': r.condition
                }
                for r in db_records
            ]
    except Exception as e:
        print(f"Error fetching history from DB: {e}")

    # Jika database masih kosong sama sekali, sediakan data default awal
    if not history_records:
        history_records = [
            {
                'id': 'M-0003',
                'raw_id': 3,
                'date': '30 Sep, 09:42',
                'machine_type': 'L',
                'air_temp': 298.1,
                'process_temp': 308.6,
                'rotational_speed': 1551,
                'torque': 42.8,
                'tool_wear': 120,
                'failure_pred': 'Normal',
                'failure_prob': 12.4,
                'cluster': 1,
                'cluster_condition': 'Kondisi Operasi Optimal'
            },
            {
                'id': 'M-0002',
                'raw_id': 2,
                'date': '30 Sep, 08:15',
                'machine_type': 'M',
                'air_temp': 301.5,
                'process_temp': 311.2,
                'rotational_speed': 1310,
                'torque': 69.4,
                'tool_wear': 215,
                'failure_pred': 'Failure Risk',
                'failure_prob': 78.2,
                'cluster': 2,
                'cluster_condition': 'Putaran Tinggi, Torsi Rendah'
            },
            {
                'id': 'M-0001',
                'raw_id': 1,
                'date': '29 Sep, 16:30',
                'machine_type': 'H',
                'air_temp': 297.8,
                'process_temp': 308.1,
                'rotational_speed': 1580,
                'torque': 38.2,
                'tool_wear': 45,
                'failure_pred': 'Normal',
                'failure_prob': 8.7,
                'cluster': 0,
                'cluster_condition': 'Suhu Operasi Tinggi'
            }
        ]

    total_count = len(history_records)
    normal_count = sum(1 for r in history_records if 'normal' in str(r['failure_pred']).lower() or float(r['failure_prob']) < 50.0)
    high_risk_count = total_count - normal_count
    normal_pct = round((normal_count / total_count * 100), 1) if total_count > 0 else 100.0
    high_risk_pct = round((high_risk_count / total_count * 100), 1) if total_count > 0 else 0.0

    return render_template(
        'history.html',
        records=history_records,
        total_count=total_count,
        normal_count=normal_count,
        high_risk_count=high_risk_count,
        normal_pct=normal_pct,
        high_risk_pct=high_risk_pct
    )

