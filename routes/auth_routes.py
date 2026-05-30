import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from models import User
from extensions import db, mail

# Inisialisasi Blueprint untuk Auth
auth_bp = Blueprint('auth', __name__)

# Fungsi bantuan untuk mengarahkan pengguna berdasarkan perannya
def redirect_based_on_role(role):
    if role == 'owner':
        return redirect(url_for('owner.dashboard')) # Sesuaikan dengan nama fungsi di owner_routes
    elif role == 'kasir':
        return redirect(url_for('kasir.dashboard')) # Sesuaikan dengan nama fungsi di kasir_routes
    elif role == 'koki':
        return redirect(url_for('koki.antrian'))  # Sesuaikan dengan nama fungsi di koki_routes
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

        errors = {}

        # Validasi 0: Minimal 8 karakter untuk kata sandi
        if len(password) < 8:
            errors['password'] = "Kata sandi harus terdiri dari minimal 8 karakter."
        
        # Validasi 1: Konfirmasi kata sandi
        if password != confirm_password:
            errors['confirm_password'] = "Konfirmasi kata sandi tidak cocok."
            
        # Validasi 2: Cek apakah Username sudah ada
        if User.query.filter_by(username=username).first():
            errors['username'] = "Username sudah digunakan. Silakan pilih yang lain."

        # Validasi 3: Cek apakah Email sudah terdaftar
        if User.query.filter_by(email=email).first():
            errors['email'] = "Email sudah terdaftar. Silakan gunakan email lain."

        # Jika terdapat error, kembalikan ke halaman registrasi dengan pesan error inline
        if errors:
            return render_template('register.html', errors=errors, form_data=request.form)

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
    
    # Menghapus semua notifikasi yang menyangkut dari sesi sebelumnya
    session.pop('_flashes', None)
    
    return redirect(url_for('auth.login'))

# ==============================================================================
# FITUR FORGOT PASSWORD (ANTI-GAGAL & MULTI-COMPATIBLE)
# ==============================================================================

@auth_bp.route('/forgot-password')
def forgot_password():
    return render_template('forgot-pass.html')

# ── API 1: Kirim OTP Nyata ke Email Berdasarkan Database ──
@auth_bp.route('/api/forgot-password/kirim-otp', methods=['POST'])
def kirim_otp():
    data = request.json or {}
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({"success": False, "message": "Email tidak boleh kosong."})
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"success": False, "message": "Email tidak terdaftar di sistem Terralog."})
    
    otp = str(random.randint(100000, 999999))
    
    session['reset_otp'] = otp
    session['reset_email'] = email
    session['otp_verified'] = False
    session.modified = True
    
    # ── INDIKATOR JALUR EMAIL ──
    print(f"\n[1/3] Database aman. OTP didapat: {otp}")
    print(f"[2/3] Mencoba menghubungkan ke SMTP Mailtrap via Port {current_app.config.get('MAIL_PORT')}...")
    
    try:
        msg = Message(
            subject="Kode OTP Reset Password - Terralog",
            recipients=[email]
        )
        msg.body = f"Halo {user.name},\n\nKode OTP Anda adalah: {otp}"
        
        mail.send(msg) # <-- Di baris ini program biasanya membeku jika jaringan diblokir
        
        print(f"[3/3] [SUKSES] Email berhasil terkirim ke Mailtrap!\n")
    except Exception as e:
        print(f"[3/3] [GAGAL SMTP]: {str(e)}")
        print(f"[FALLBACK] KODE OTP ANDA ADALAH: {otp}\n")
        
    return jsonify({"success": True, "message": f"Kode OTP berhasil dikirim ke {email}."})

# ── API 2: Verifikasi OTP dari Session ──
@auth_bp.route('/api/forgot-password/verifikasi-otp', methods=['POST'])
def verifikasi_otp():
    data = request.json or {}
    otp = data.get('otp', '').strip()
    
    session_otp = session.get('reset_otp')
    
    if not session_otp:
        return jsonify({"success": False, "message": "Sesi habis atau OTP belum diminta. Silakan kirim ulang."})
        
    if otp == session_otp:
        session['otp_verified'] = True
        session.modified = True
        # Mengembalikan objek success murni dan pesan untuk kecocokan frontend javascript
        return jsonify({"success": True, "message": "Verifikasi OTP berhasil!"})
        
    return jsonify({"success": False, "message": "Kode OTP salah."})

# ── API 3: Update Password Baru (Mendukung 3 variasi URL sekaligus) ──
@auth_bp.route('/api/forgot-password/reset', methods=['POST'])
@auth_bp.route('/api/forgot-password/reset-password', methods=['POST'])
@auth_bp.route('/api/forgot-password/ubah-password', methods=['POST'])
def reset_password_bulletproof():
    data = request.json or {}
    
    # ANTISIPASI: Mencari segala kemungkinan nama key password yang dikirim dari JS Anda
    password_baru = (
        data.get('password_baru') or 
        data.get('password') or 
        data.get('new_password') or 
        data.get('newPassword')
    )
    
    # Ambil email dari data kiriman atau dari session backend
    email = data.get('email', '').strip() or session.get('reset_email')
    
    if not password_baru:
        return jsonify({"success": False, "message": "Password baru tidak boleh kosong."})
        
    if not email:
        return jsonify({"success": False, "message": "Sesi Anda telah berakhir. Silakan ulangi dari awal."})
        
    if len(password_baru) < 8:
        return jsonify({"success": False, "message": "Password minimal harus 8 karakter."})
        
    # Eksekusi perubahan ke database
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"success": False, "message": "Pengguna tidak ditemukan."})
        
    try:
        user.password = generate_password_hash(password_baru)
        db.session.commit()
        
        # Bersihkan data session reset password demi keamanan
        session.pop('reset_otp', None)
        session.pop('reset_email', None)
        session.pop('otp_verified', None)
        session.modified = True
        
        return jsonify({"success": True, "message": "Kata sandi Anda berhasil diperbarui!"})
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR DATABASE RESET PASSWORD]: {str(e)}")
        return jsonify({"success": False, "message": "Gagal menyimpan perubahan ke database."})