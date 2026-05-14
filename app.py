import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from extensions import db, login_manager
from models import User
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError

# load_dotenv() 

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)

@app.errorhandler(OperationalError)
def handle_db_error(e):
    # Logika: Jika error mengandung indikasi gagal koneksi ke MySQL
    return """
    <div style="text-align: center; padding: 50px; font-family: sans-serif;">
        <h1 style="color: #e74c3c;">Database Belum Aktif!</h1>
        <p>Sepertinya <strong>Laragon/XAMPP</strong> belum dinyalakan atau MySQL mati.</p>
        <p>Pastikan modul MySQL di control panel sudah berwarna hijau (Running).</p>
        <button onclick="location.reload()">Refresh Halaman</button>
    </div>
    """, 503

# ==========================================
# KONFIGURASI DATABASE
# ==========================================
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_DATABASE")
APP_USER = os.getenv("DB_APP_USERNAME")
APP_PASS = os.getenv("DB_APP_PASSWORD")

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{APP_USER}:{APP_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

db.init_app(app)

# ==========================================
# KONFIGURASI FLASK-LOGIN
# ==========================================
login_manager.init_app(app)
login_manager.login_view = 'auth.login' # Arahkan ke rute login jika belum autentikasi
login_manager.login_message = "Silakan login terlebih dahulu untuk mengakses halaman ini."

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

from models import *

# ==========================================
# REGISTRASI BLUEPRINT (ROUTES)
# ==========================================
from routes.auth_routes import auth_bp
from routes.kasir_routes import kasir_bp
from routes.customer_routes import customer_bp
from routes.owner_routes import owner_bp
from routes.koki_routes import koki_bp

app.register_blueprint(auth_bp)
app.register_blueprint(kasir_bp, url_prefix='/kasir')
app.register_blueprint(customer_bp, url_prefix='/customer')
app.register_blueprint(owner_bp, url_prefix='/owner')
app.register_blueprint(koki_bp, url_prefix='/koki')

print(app.url_map)

# ==========================================
# ROUTING UTAMA & MOCK DATA
# ==========================================
@app.route('/')
def home():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, port=50001)
