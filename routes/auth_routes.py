from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from extensions import db

# Inisialisasi Blueprint untuk Auth
auth_bp = Blueprint('auth', __name__)

# Fungsi bantuan untuk mengarahkan pengguna berdasarkan perannya
def redirect_based_on_role(role):
    if role == 'owner':
        return redirect(url_for('owner.dashboard')) # Sesuaikan dengan nama fungsi di owner_routes
    elif role == 'kasir':
        return redirect(url_for('kasir.dashboard')) # Sesuaikan dengan nama fungsi di kasir_routes
    elif role == 'koki':
        return redirect(url_for('koki.dashboard'))  # Sesuaikan dengan nama fungsi di koki_routes
    else:
        return redirect(url_for('customer.beranda')) # Sesuaikan dengan nama fungsi di customer_routes

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Jika pengguna sudah login, arahkan langsung ke halaman mereka
    if current_user.is_authenticated:
        return redirect_based_on_role(current_user.role)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Cari pengguna di database
        user = User.query.filter_by(username=username).first()
        
        # Verifikasi pengguna dan kecocokan kata sandi
        if user and check_password_hash(user.password, password):
            if not user.is_active:
                flash("Akun Anda dinonaktifkan.", "danger")
                return redirect(url_for('auth.login'))
                
            login_user(user)
            return redirect_based_on_role(user.role)
        else:
            flash("Username atau password salah.", "danger")
    
    # Render template login dari root folder templates
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect_based_on_role(current_user.role)
    
    if request.method == 'POST':
        username = request.form.get('username')
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validasi 1: Konfirmasi kata sandi
        if password != confirm_password:
            flash("Konfirmasi kata sandi tidak cocok.", "warning")
            return redirect(url_for('auth.register'))
            
        # Validasi 2: Cek apakah Username sudah ada
        if User.query.filter_by(username=username).first():
            flash("Username sudah digunakan. Silakan pilih yang lain.", "warning")
            return redirect(url_for('auth.register'))

        # Validasi 3: Cek apakah Email sudah terdaftar
        if User.query.filter_by(email=email).first():
            flash("Email sudah terdaftar. Silakan gunakan email lain atau langsung masuk.", "warning")
            return redirect(url_for('auth.register'))

        # Enkripsi kata sandi sebelum disimpan ke database
        hashed_password = generate_password_hash(password)
        
        # Buat pengguna baru (secara default registrasi publik biasanya menjadi 'customer')
        new_user = User(
            username=username, 
            name=fullname, 
            email=email, 
            password=hashed_password, 
            role='customer',
            is_active=True
        )
        
        # Proses simpan ke database yang aman (Try-Except)
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Jika berhasil, arahkan ke login dan munculkan notifikasi sukses hijau
            flash("Registrasi berhasil. Silakan masuk.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR DATABASE REGISTER]: {str(e)}")
            flash("Terjadi kesalahan pada sistem. Pendaftaran gagal.", "danger")
            return redirect(url_for('auth.register'))
        
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))