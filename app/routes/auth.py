from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Harap masukkan email dan kata sandi.', 'warning')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            return redirect(url_for('main.dashboard'))

        flash('Email atau kata sandi salah. Silakan coba lagi.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not email or not password:
            flash('Harap isi semua bidang pendaftaran.', 'warning')
            return render_template('login.html')

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username atau email sudah terdaftar.', 'warning')
            return render_template('login.html')

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Pendaftaran berhasil! Silakan masuk.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
