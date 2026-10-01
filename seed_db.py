"""
Script untuk mengisi database PostgreSQL dengan data dummy simpel (Users & Machine Analyses)
"""
import os
from werkzeug.security import generate_password_hash
from app import create_app
from app.models import db, User, MachineAnalysis
from datetime import datetime, timedelta

app = create_app()

def seed_database():
    with app.app_context():
        # Buat tabel jika belum ada
        db.create_all()

        print("--> Mengosongkan data dummy lama untuk reset simpel...")
        MachineAnalysis.query.delete()
        User.query.delete()
        db.session.commit()

        print("--> Menambahkan data pengguna dummy simpel...")
        users_data = [
            {
                "username": "admin",
                "email": "admin@email.com",
                "password": "123"
            },
            {
                "username": "user",
                "email": "user@email.com",
                "password": "123"
            },
            {
                "username": "operator",
                "email": "operator@email.com",
                "password": "123"
            }
        ]

        seeded_users = []
        for u in users_data:
            new_user = User(
                username=u["username"],
                email=u["email"],
                password_hash=generate_password_hash(u["password"])
            )
            db.session.add(new_user)
            seeded_users.append(new_user)
            print(f"    [+] User dibuat: {u['username']} | Email: {u['email']} | Password: {u['password']}")

        db.session.commit()

        # Seed beberapa riwayat analisis mesin untuk user pertama
        primary_user = seeded_users[0]
        print("--> Mengisi data riwayat analisis mesin...")
        sample_records = [
            {
                "machine_type": "L",
                "air_temp": 298.1,
                "process_temp": 308.6,
                "rotational_speed": 1551,
                "torque": 42.8,
                "tool_wear": 120,
                "failure_pred": "Normal",
                "failure_prob": 12.4,
                "cluster": 1,
                "condition": "Medium Operating Condition",
                "action": "Inspect",
                "q_value": 6.82,
                "created_at": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "machine_type": "M",
                "air_temp": 301.5,
                "process_temp": 311.2,
                "rotational_speed": 1310,
                "torque": 69.4,
                "tool_wear": 215,
                "failure_pred": "Failure Risk",
                "failure_prob": 78.2,
                "cluster": 2,
                "condition": "High Load Condition",
                "action": "Maintenance",
                "q_value": 8.92,
                "created_at": datetime.utcnow() - timedelta(hours=4)
            },
            {
                "machine_type": "H",
                "air_temp": 297.8,
                "process_temp": 308.1,
                "rotational_speed": 1580,
                "torque": 38.2,
                "tool_wear": 45,
                "failure_pred": "Normal",
                "failure_prob": 8.7,
                "cluster": 0,
                "condition": "Optimal Operating Condition",
                "action": "Continue",
                "q_value": 9.45,
                "created_at": datetime.utcnow() - timedelta(days=1)
            }
        ]

        for rec in sample_records:
            record = MachineAnalysis(
                user_id=primary_user.id,
                machine_type=rec["machine_type"],
                air_temp=rec["air_temp"],
                process_temp=rec["process_temp"],
                rotational_speed=rec["rotational_speed"],
                torque=rec["torque"],
                tool_wear=rec["tool_wear"],
                failure_pred=rec["failure_pred"],
                failure_prob=rec["failure_prob"],
                cluster=rec["cluster"],
                condition=rec["condition"],
                action=rec["action"],
                q_value=rec["q_value"],
                created_at=rec["created_at"]
            )
            db.session.add(record)
        db.session.commit()
        print("    [+] Riwayat analisis berhasil diisi!")

        print("--> Database Seeding Selesai dengan Sukses!")

if __name__ == "__main__":
    seed_database()
