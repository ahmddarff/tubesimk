import os
import random
import string
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash, current_app
from flask_login import login_required, current_user

from models import User, Menu, Category, Order, OrderItem, Table
from extensions import db

customer_bp = Blueprint('customer', __name__)

# =========================
# BERANDA & MENU
# =========================

@customer_bp.route('/')
def beranda():
    return render_template('customer/beranda.html', segment='customer', role='customer')

@customer_bp.route('/daftar-menu')
def daftar_menu():
    # Mengambil semua data kategori dan menu dari basis data
    categories = Category.query.all()
    menus = Menu.query.all()
    
    return render_template('customer/daftar_menu.html', 
                        menu=menus, 
                        categories=categories, 
                        segment='daftar_menu', 
                        role='customer')

@customer_bp.route('/menu/<int:menu_id>')
def menu_detail(menu_id):
    # Mengambil data menu dari basis data berdasarkan ID
    menu = Menu.query.get_or_404(menu_id)
    
    return render_template('customer/menu_detail.html', 
             menu=menu, 
             segment='daftar_menu', 
             role='customer')


# =========================
# RESERVASI
# =========================

@customer_bp.route('/buat-reservasi')
def buat_reservasi():
    # Data statis untuk tampilan (dapat diganti query database nantinya)
    active_reservations = [
        {
            "id": "AB123", "status": "Menunggu", "date": "06 April 2026",
            "time": "15:15 WIB", "duration": "2 Jam", "guests": "21"
        }
    ]
    
    history_reservations = [
        {
            "id": "AB650", "status": "Selesai", "date": "05 April 2026",
            "time": "16:00 WIB", "duration": "1 Jam", "guests": "2"
        },
        {
            "id": "AC780", "status": "Dibatalkan", "date": "06 Desember 2025",
            "time": "08:00 WIB", "duration": "2+ Jam", "guests": "134"
        }
    ]
    
    return render_template('customer/buat_reservasi.html', 
                 segment='buat_reservasi', 
                 role='customer', 
                 active_reservations=active_reservations, 
                 history_reservations=history_reservations)

@customer_bp.route('/buat-reservasi/submit', methods=['POST'])
def submit_buat_reservasi():
    # Mengambil data dari formulir
    tanggal = request.form.get('tanggal')
    waktu = request.form.get('waktu')
    jumlah_tamu = request.form.get('jumlah_tamu')
    meja = request.form.get('meja')
    
    # Generate ID Reservasi acak
    reservasi_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Formatisasi tampilan tanggal
    tanggal_display = ""
    if tanggal:
        date_obj = datetime.strptime(tanggal, '%Y-%m-%d')
        day_names = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']
        month_names = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        day_name = day_names[date_obj.weekday()]
        month_name = month_names[date_obj.month - 1]
        tanggal_display = f'{date_obj.day:02d} {month_name} {date_obj.year} ({day_name})'
    
    # Formatisasi tampilan waktu (asumsi durasi 2 jam)
    waktu_display = waktu
    if waktu:
        try:
            time_obj = datetime.strptime(waktu, '%H:%M')
            end_hour = (time_obj.hour + 2) % 24
            waktu_display = f'{time_obj.strftime("%H:%M")} - {end_hour:02d}:00 WIB'
        except:
            pass
    
    return render_template('customer/reservasi_detail.html', 
                         nama='Matthew Shen',
                         nomor='08123457890',
                         meja=meja,
                         tanggal_display=tanggal_display,
                         waktu_display=waktu_display,
                         jumlah_tamu=jumlah_tamu,
                         reservasi_id=reservasi_id,
                         segment='buat_reservasi',
                         role='customer')

@customer_bp.route('/reservasi/new')
def reservasi_new():
    return render_template('customer/buat_reservasi_new.html', segment='buat_reservasi', role='customer')

@customer_bp.route('/reservasi/<reservation_id>')
def reservasi_detail(reservation_id):
    return render_template('customer/reservasi_detail.html', segment='buat_reservasi', role='customer', reservation_id=reservation_id)

@customer_bp.route('/reservasi/history')
def reservasi_history():
    history_reservations = [
        {"id": "AB650", "status": "Selesai", "date": "05 April 2026", "time": "16:00 WIB", "duration": "1 Jam", "guests": "2"},
        {"id": "AC780", "status": "Dibatalkan", "date": "06 Desember 2025", "time": "08:00 WIB", "duration": "2+ Jam", "guests": "134"},
        {"id": "AB456", "status": "Selesai", "date": "15 Maret 2026", "time": "19:30 WIB", "duration": "3 Jam", "guests": "5"}
    ]
    return render_template('customer/reservasi_history.html', segment='buat_reservasi', role='customer', history_reservations=history_reservations)


# =========================
# MANAJEMEN PESANAN & CHECKOUT
# =========================

@customer_bp.route('/pesanan-saya')
@login_required
def pesanan_saya():
    # Mengambil semua pesanan milik user yang sedang login
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    # Memisahkan pesanan Aktif dan Riwayat
    active_orders = [o for o in user_orders if o.order_status != 'served' or o.payment_status == 'unpaid']
    history_orders = [o for o in user_orders if (o.order_status == 'served' and o.payment_status == 'paid') or o.payment_status == 'cancelled']
    
    return render_template('customer/pesanan_saya.html', 
                            segment='pesanan_saya', 
                            role='customer', 
                            active_orders=active_orders, 
                            history_orders=history_orders)

@customer_bp.route('/pesanan-saya/history')
def pesanan_history():
    # Data statis riwayat pesanan
    history_orders = [
        {
            "id": "AB098", "status": "Selesai", "date": "14 Februari 2026", "time": "21:48 WIB",
            "products": [{"nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "qty": 2}],
            "total": 38000
        },
        {
            "id": "AB073", "status": "Dibatalkan", "date": "13 Januari 2026", "time": "17:45 WIB",
            "products": [{"nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "qty": 1}],
            "total": 18000
        }
    ]
    return render_template('customer/pesanan_history.html', segment='pesanan_saya', role='customer', history_orders=history_orders)

@customer_bp.route('/checkout')
def checkout():
    # Mengambil item yang mungkin sudah diisi sebelumnya (dari fitur pesan-lagi)
    pre_filled_items = session.get('pre_filled_items', None)
    session.pop('pre_filled_items', None) 
    session.modified = True
    
    return render_template('customer/checkout.html', segment='checkout', role='customer', pre_filled_items=pre_filled_items)

@customer_bp.route('/pesan-lagi/<order_id>')
def pesan_lagi(order_id):
    # Logika sederhana untuk mengambil data pesanan lama dan memasukkannya kembali ke keranjang/checkout
    history_orders = [
        {"id": "AB098", "products": [{"nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "qty": 2}]},
        {"id": "AB073", "products": [{"nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "qty": 1}]}
    ]
    
    order = next((o for o in history_orders if o['id'] == order_id), None)
    if order is None:
        return redirect(url_for('customer.pesanan_history'))
    
    session['pre_filled_items'] = order['products']
    session.modified = True
    return redirect(url_for('customer.checkout'))

@customer_bp.route('/submit-order', methods=['POST'])
def submit_order():
    data = request.get_json()
    order_id = 'AB' + ''.join(random.choices(string.digits, k=3))
    
    # Simpan sementara di session (untuk demo/prototype)
    if 'orders' not in session:
        session['orders'] = {}
    
    session['orders'][order_id] = {
        'order_id': order_id,
        'nama': data.get('nama'),
        'meja': data.get('meja'),
        'items': data.get('items'),
        'paymentMethod': data.get('paymentMethod'),
        'total': data.get('total'),
        'subtotal': data.get('subtotal'),
        'ppn': data.get('ppn'),
        'created_at': datetime.now().strftime('%d %B %Y %H:%M'),
        'status': 'Menunggu Pembayaran'
    }
    session.modified = True
    return jsonify({'order_id': order_id, 'success': True})

@customer_bp.route('/pesanan/<order_id>')
def pesanan_detail(order_id):
    order = session.get('orders', {}).get(order_id)
    return render_template('customer/pesanan_aktif_detail.html', segment='pesanan_saya', role='customer', order=order, order_id=order_id)

@customer_bp.route('/pesanan/<order_id>/selesai')
def pesanan_selesai(order_id):
    if 'orders' in session and order_id in session['orders']:
        session['orders'][order_id]['status'] = 'Selesai'
        session.modified = True
    
    order = session.get('orders', {}).get(order_id)
    return render_template('customer/pesanan_selesai.html', segment='pesanan_saya', role='customer', order=order, order_id=order_id)

@customer_bp.route('/pembayaran-nontunai/<order_id>')
def pembayaran_nontunai(order_id):
    return render_template('customer/pembayaran_nontunai.html', segment='pembayaran', role='customer', order_id=order_id)


# =========================
# PENGATURAN PROFIL
# =========================

@customer_bp.route('/pengaturan', methods=['GET', 'POST'])
@login_required
def pengaturan():
    if request.method == 'POST':
        # Update data teks
        current_user.name = request.form.get('name')
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')

        # Logika Upload Foto Profil
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                if current_user.photo:
                    old_path = os.path.join(current_app.root_path, 'static/images', current_user.photo)
                    if os.path.exists(old_path) and os.path.isfile(old_path):
                        try: os.remove(old_path)
                        except: pass
                
                filename = secure_filename(file.filename)
                unique_filename = f"user_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file.save(os.path.join(current_app.root_path, 'static/images', unique_filename))
                current_user.photo = unique_filename

        try:
            db.session.commit()
            flash('Profil berhasil diperbarui!', 'success')
        except Exception:
            db.session.rollback()
            flash('Gagal memperbarui profil. Username/Email mungkin sudah digunakan.', 'danger')
        
        return redirect(url_for('customer.pengaturan'))

    return render_template('customer/pengaturan.html', segment='pengaturan', role='customer', user=current_user)

@customer_bp.route('/api/update-password', methods=['POST'])
@login_required
def update_password():
    data = request.json
    if not check_password_hash(current_user.password, data.get("password_lama")):
        return jsonify({"success": False, "message": "Kata sandi saat ini salah!"})
    
    current_user.password = generate_password_hash(data.get("password_baru"))
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Kata sandi berhasil diperbarui!"})
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Gagal menyimpan kata sandi."})