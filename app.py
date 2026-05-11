import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from extensions import db
from dotenv import load_dotenv

load_dotenv() 

app = Flask(__name__)

# ==========================================
# KONFIGURASI DATABASE (HANYA APP URI)
# ==========================================
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_DATABASE")
APP_USER = os.getenv("DB_APP_USERNAME")
APP_PASS = os.getenv("DB_APP_PASSWORD")

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{APP_USER}:{APP_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

db.init_app(app)

from models import *

# ==========================================
# REGISTRASI BLUEPRINT (ROUTES)
# ==========================================
# Import blueprint dari folder routes
from routes.auth_routes import auth_bp
from routes.kasir_routes import kasir_bp
from routes.customer_routes import customer_bp
from routes.owner_routes import owner_bp
from routes.koki_routes import koki_bp

# Daftarkan blueprint ke aplikasi Flask
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
    # Karena root web biasanya langsung ke login, kita redirect menggunakan nama fungsi di dalam blueprint
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, port=50001)