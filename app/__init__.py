from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-key-predictive-maintenance'

    @app.route('/')
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    return app
    