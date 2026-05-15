import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import Menu, Reservation, Order, OrderItem
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

kasir_bp = Blueprint('kasir', __name__)

# =========================
# DASHBOARD
# =========================
@kasir_bp.route('/dashboard')
@login_required
def dashboard():
    # Mengambil seluruh data menu dari database
    menus_db = Menu.query.all()
    
    menu_list = []
    for m in menus_db:
        # Menentukan status ketersediaan berdasarkan kolom is_available dan stock
        # Jika stok adalah None (untuk makanan/minuman yang selalu bisa dimasak) 
        # atau lebih dari 0, dan status is_available adalah True, maka menu tersedia.
        if m.is_available and (m.stock is None or m.stock > 0):
            status_menu = 'tersedia'
        else:
            status_menu = 'habis'
            
        menu_list.append({
            "id": m.id,
            "nama": m.name,
            "harga": m.price,
            # Menetapkan gambar bawaan apabila image_url pada database kosong
            "img": m.image_url if m.image_url else "gambar.png", 
            "status": status_menu,
            # Karena model Menu belum memiliki atribut rating, nilai ini dapat 
            # dibuat statis untuk sementara waktu.
            "rating": "4.8" 
        })

    return render_template(
        'kasir/dashboard.html', 
        username=current_user.name,
        segment='dashboard',
        role='kasir',
        menu=menu_list
    )


# =========================
# PESANAN AKTIF
# =========================
@kasir_bp.route('/pesanan-aktif')
def pesanan_aktif():
    pesanan_list = [
        {"id": "P052", "nama": "Agnes", "meja": "07", "status": "PENDING", "total": 48000, "waktu": "12.12", "tipe": "DINE IN"},
        {"id": "P051", "nama": "Joy", "meja": "-", "status": "PENDING", "total": 48000, "waktu": "11.56", "tipe": "TAKE AWAY"},
        {"id": "P049", "nama": "Rahma", "meja": "06", "status": "READY", "total": 48000, "waktu": "11.27", "tipe": "DINE IN"},
        {"id": "P045", "nama": "Sonya", "meja": "03", "status": "SERVED", "total": 48000, "waktu": "10.40", "tipe": "DINE IN"},
    ]

    return render_template(
        'kasir/pesanan_aktif.html',
        segment='pesanan_aktif',
        role='kasir',
        pesanan=pesanan_list
    )


# =========================
# RESERVASI
# =========================
@kasir_bp.route('/reservasi')
@login_required
def reservasi():
    reservations_db = Reservation.query.all()
    data_reservasi = []

    for res in reservations_db:
        status_mapping = {
            'pending': 'Menunggu',
            'confirmed': 'Dikonfirmasi',
            'completed': 'Selesai',
            'cancelled': 'Dibatalkan'
        }

        # Menentukan nama pelanggan
        nama_pelanggan = res.customer_name or (res.user.name if res.user else "Tanpa Nama")

        # Mengambil semua nomor meja dari tabel relasi
        meja_list = [rt.table_number_snapshot for rt in res.reserved_tables]
        meja_str = ", ".join(meja_list) if meja_list else "-"

        # Menghitung jam selesai berdasarkan durasi
        jam_mulai_str = ""
        jam_selesai_str = ""
        if res.reservation_time:
            jam_mulai_str = res.reservation_time.strftime('%H:%M')
            if res.duration:
                mulai_dt = datetime.combine(datetime.today(), res.reservation_time)
                selesai_dt = mulai_dt + timedelta(minutes=res.duration)
                jam_selesai_str = selesai_dt.strftime('%H:%M')

        data_reservasi.append({
            'id': str(res.id).zfill(2),
            'nama': nama_pelanggan,
            'tanggal': res.reservation_date.strftime('%Y-%m-%d') if res.reservation_date else '',
            'tamu': res.guest_qty, # Menggunakan kolom baru
            'telepon': res.phone,
            'jam_mulai': jam_mulai_str,
            'jam_selesai': jam_selesai_str, # Terhitung otomatis
            'status': status_mapping.get(res.status, 'Menunggu'),
            'meja': meja_str # Sekarang bisa menampilkan lebih dari 1 meja (contoh: "03, 04")
        })

    return render_template(
        'kasir/reservasi.html',
        segment='reservasi',
        role='kasir',
        reservations=data_reservasi
    )


# =========================
# RIWAYAT TRANSAKSI
# =========================
@kasir_bp.route('/riwayat-transaksi')
@login_required
def riwayat_transaksi():
    # Ambil pesanan dengan status 'served' atau 'completed' (asumsi: ini adalah transaksi selesai)
    orders_db = Order.query.filter(Order.order_status.in_(['served', 'completed'])).order_by(Order.created_at.desc()).all()
    
    data_transaksi = []
    
    for order in orders_db:
        # Menyiapkan list item untuk transaksi ini
        items_list = []
        for item in order.items:
            items_list.append({
                'nama': item.menu.name if item.menu else 'Item Terhapus',
                'harga': item.price_at_order,
                'jumlah': item.qty,
                'subtotal': item.price_at_order * item.qty
            })

        # Menentukan nama pelanggan
        nama_pelanggan = order.customer_name or (order.user.name if order.user else "Tamu Anonim")
        
        # Mapping metode pembayaran (Opsional: menyesuaikan format teks)
        metode_map = {'cash': 'TUNAI', 'qris': 'QRIS'}
        metode_bayar = metode_map.get(order.payment_method, str(order.payment_method).upper())

        data_transaksi.append({
            'id': order.order_number,
            'tanggal': order.created_at.strftime('%Y-%m-%d'),
            'waktu': order.created_at.strftime('%H.%M'),
            'kasir': 'Kasir Terralog', # Sesuaikan jika Anda mencatat relasi kasir di DB
            'pelanggan': nama_pelanggan,
            'metode': metode_bayar,
            'total': order.total_amount,
            'items': items_list
        })

    return render_template('kasir/riwayat_transaksi.html', 
        segment='riwayat_transaksi', 
        transactions=data_transaksi,
        role='kasir',
    )


# =========================
# PENGATURAN
# =========================
@kasir_bp.route('/pengaturan', methods=['GET', 'POST'])
@login_required
def pengaturan():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')

        # Konsisten menggunakan 'photo'
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                upload_path = os.path.join(current_app.root_path, 'static/uploads/profile')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

                # Hapus foto lama
                if current_user.photo:
                    old_path = os.path.join(current_app.root_path, 'static', current_user.photo)
                    if not os.path.exists(old_path) and not current_user.photo.startswith('uploads/'):
                        old_path = os.path.join(current_app.root_path, 'static/images', current_user.photo)
                        
                    if os.path.exists(old_path) and os.path.isfile(old_path):
                        try: os.remove(old_path)
                        except: pass
                
                filename = secure_filename(file.filename)
                unique_filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                
                file.save(os.path.join(upload_path, unique_filename))
                
                # Simpan beserta alamat path relatifnya ke database
                current_user.photo = f"uploads/profile/{unique_filename}"

        try:
            db.session.commit()
            flash('Profil berhasil diperbarui!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Gagal memperbarui profil. Username atau email mungkin sudah digunakan.', 'danger')
        
        return redirect(url_for('kasir.pengaturan'))

    return render_template('kasir/pengaturan.html', segment='pengaturan', role='kasir', user=current_user)

@kasir_bp.route('/api/update-password', methods=['POST'])
@login_required
def update_password():
    data = request.json
    password_lama = data.get("password_lama")
    password_baru = data.get("password_baru")
    
    # Verifikasi kata sandi saat ini
    if not check_password_hash(current_user.password, password_lama):
        return jsonify({"success": False, "message": "Kata sandi saat ini salah!"})
    
    # Enkripsi dan simpan kata sandi baru
    current_user.password = generate_password_hash(password_baru)
    
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Kata sandi berhasil diperbarui!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Gagal menyimpan kata sandi baru."})