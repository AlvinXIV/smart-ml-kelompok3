from flask import Blueprint, render_template, request, redirect, url_for, flash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        if email and password:
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        if username and email and password:
            return redirect(url_for('auth.login'))
        flash('Please fill in all required fields.', 'warning')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    return redirect(url_for('auth.login'))
