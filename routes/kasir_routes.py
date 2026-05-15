import os
from datetime import date
from utils import *
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import Menu, Reservation, Order, OrderItem, Table
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
    # ==========================================
    # 1. DATA STATISTIK (CARD ATAS)
    # ==========================================
    today = date.today()

    # Statistik Meja (Hanya menghitung jumlahnya saja)
    total_meja = Table.query.count()
    meja_kosong = Table.query.filter_by(is_available=True).count()

    # Statistik Pesanan Hari Ini
    pesanan_aktif = Order.query.filter(
        Order.order_status.in_(['pending', 'preparing', 'ready']),
        db.func.date(Order.created_at) == today
    ).count()

    belum_lunas = Order.query.filter(
        Order.payment_status == 'unpaid',
        db.func.date(Order.created_at) == today
    ).count()

    selesai = Order.query.filter(
        Order.order_status == 'served',
        db.func.date(Order.created_at) == today
    ).count()

    # Digabungkan untuk dipanggil di HTML loop
    stats_data = [
        ('Meja Kosong', f"{meja_kosong}/{total_meja}"),
        ('Pesanan Aktif', str(pesanan_aktif)),
        ('Belum Lunas', str(belum_lunas)),
        ('Selesai', str(selesai))
    ]
    
    # ==========================================
    # 2. DATA TRANSAKSI (KERANJANG & KATALOG)
    # ==========================================
    # Mengambil objek meja yang tersedia untuk dropdown pilihan kasir
    tables_db = Table.query.filter_by(is_available=True).order_by(Table.table_number).all()
    
    # Mengambil dan memformat data menu untuk katalog
    menus_db = Menu.query.all()
    menu_list = []
    
    for m in menus_db:
        # Cek ketersediaan berdasarkan saklar is_available dan sisa stok
        if m.is_available and (m.stock is None or m.stock > 0):
            status_menu = 'tersedia'
        else:
            status_menu = 'habis'
            
        menu_list.append({
            "id": m.id,
            "nama": m.name,
            "harga": m.price,
            "img": m.image_url if m.image_url else "gambar.png", 
            "status": status_menu
        })

    # ==========================================
    # 3. LOGIKA MODE EDIT PESANAN
    # ==========================================
    edit_order_id = request.args.get('edit')
    edit_data = None

    if edit_order_id:
        order_to_edit = Order.query.filter_by(order_number=edit_order_id).first()
        if order_to_edit:
            cart_items = []
            for item in order_to_edit.items:
                cart_items.append({
                    "id": item.menu_id,
                    "nama": item.menu.name if item.menu else "Menu Dihapus",
                    "harga": item.price_at_order,
                    "qty": item.qty,
                    "note": item.notes or "",
                    "img": item.menu.image_url if item.menu and item.menu.image_url else "gambar.png",
                    "status": item.item_status # Penting untuk menandai mana yang sudah dimasak
                })
            
            edit_data = {
                "order_number": order_to_edit.order_number,
                "customer_name": order_to_edit.customer_name,
                "table_id": order_to_edit.table_id,
                "order_type": "dine-in" if order_to_edit.order_type == "dine_in" else "takeaway",
                "cart": cart_items,
                "lunas": True if order_to_edit.payment_status == 'paid' else False
            }

    # ==========================================
    # 4. RENDER TEMPLATE
    # ==========================================
    return render_template(
        'kasir/dashboard.html', 
        segment='dashboard',
        role='kasir',
        stats=stats_data,
        tables=tables_db,
        menu=menu_list,
        edit_data=edit_data
    )

# =========================
# PESANAN AKTIF
# =========================
@kasir_bp.route('/pesanan-aktif')
@login_required
def pesanan_aktif():
    # ==========================================
    # 1. LOGIKA PERHITUNGAN STATISTIK (HARI INI)
    # ==========================================
    today = date.today()

    # Statistik Meja (Kosong / Total)
    total_meja = Table.query.count()
    meja_kosong = Table.query.filter_by(is_available=True).count()

    # Statistik Pesanan Aktif: yang sedang diproses dapur atau siap saji
    pesanan_aktif_count = Order.query.filter(
        Order.order_status.in_(['pending', 'preparing', 'ready']),
        db.func.date(Order.created_at) == today
    ).count()

    # Statistik Belum Lunas
    belum_lunas_count = Order.query.filter(
        Order.payment_status == 'unpaid',
        db.func.date(Order.created_at) == today
    ).count()

    # Statistik Selesai: menggunakan status 'served' (sudah disajikan)
    selesai_count = Order.query.filter(
        Order.order_status == 'served',
        db.func.date(Order.created_at) == today
    ).count()

    # Dikemas ke dalam list tuple untuk looping di HTML
    data_statistik = [
        ('Meja Kosong', f"{meja_kosong}/{total_meja}"),
        ('Pesanan Aktif', str(pesanan_aktif_count)),
        ('Belum Lunas', str(belum_lunas_count)),
        ('Selesai', str(selesai_count))
    ]
    
    # ==========================================
    # 2. MENGAMBIL DAFTAR PESANAN UNTUK KARTU
    # ==========================================
    # Tampilkan pesanan jika memenuhi salah satu syarat ini:
    # Syarat A: Statusnya masih diproses dapur (pending, preparing, ready)
    # Syarat B: ATAU statusnya sudah disajikan (served) TAPI belum dibayar (unpaid)
    orders_db = Order.query.filter(
        db.or_(
            Order.order_status.in_(['pending', 'preparing', 'ready']),
            db.and_(Order.order_status == 'served', Order.payment_status == 'unpaid')
        )
    ).order_by(Order.created_at.asc()).all()
    
    pesanan_aktif_data = []
    
    for order in orders_db:
        # Menyiapkan daftar menu per pesanan
        items_list = []
        for item in order.items:
            items_list.append({
                'nama': item.menu.name if item.menu else 'Item Tidak Dikenal',
                'qty': item.qty,
                'harga': item.price_at_order,
                'catatan': item.notes or '',
                'status': item.item_status
            })

        tipe_map = {'dine_in': 'DINE IN', 'take_away': 'TAKE AWAY'}
        nama_pelanggan = order.customer_name or (order.user.name if order.user else "Tamu")

        # Menyiapkan waktu ISO untuk timer real-time di frontend
        # Tambahkan 'Z' agar JavaScript mendeteksi ini sebagai waktu UTC (sesuai models.py)
        waktu_iso_str = order.created_at.isoformat() + 'Z'

        pesanan_aktif_data.append({
            'id': order.order_number,
            'nama': nama_pelanggan,
            'waktu_asli': order.created_at.strftime('%H:%M'),
            'waktu_iso': waktu_iso_str, # Digunakan oleh Alpine.js timeAgo()
            'tipe': tipe_map.get(order.order_type, 'DINE IN'),
            'meja': order.table_number_snapshot or '-',
            'status': str(order.order_status).upper(), 
            'total': order.total_amount,
            'lunas': True if order.payment_status == 'paid' else False,
            'items': items_list
        })

    # ==========================================
    # 3. RENDER KE TEMPLATE
    # ==========================================
    return render_template(
        'kasir/pesanan_aktif.html', 
        segment='pesanan_aktif', 
        pesanan=pesanan_aktif_data,
        statistik=data_statistik,
        role='kasir' 
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
    
# ── Dashboard APIs ─────────────────────────────────────────
@kasir_bp.route('/api/submit-order', methods=['POST'])
@login_required
def submit_order():
    data = request.json
    cart = data.get('cart', [])
    
    if not cart:
        return jsonify({"success": False, "message": "Keranjang kosong!"})

    try:
        # 1. GENERATE NOMOR PESANAN BERURUTAN
        order_number = generate_order_number()

        # LOGIKA METODE PEMBAYARAN AMAN
        payment_method_raw = data.get('payment_method')
        safe_payment_method = payment_method_raw.lower() if payment_method_raw else None
        
        if safe_payment_method == 'qris':
            pay_status = 'paid'
        else:
            pay_status = 'unpaid'

        # ==========================================
        # PERBAIKAN: LOGIKA UPDATE STATUS MEJA & SNAPSHOT
        # ==========================================
        table_id = data.get('table_id') if data.get('order_type') == 'dine_in' else None
        table_snapshot = None

        if table_id:
            table_obj = db.session.get(Table, table_id)
            if table_obj:
                # Ubah status meja menjadi terpakai (tidak tersedia)
                table_obj.is_available = False
                # Simpan nomor meja saat ini untuk riwayat pesanan
                table_snapshot = table_obj.table_number
        # ==========================================

        # 2. Buat Objek Order
        new_order = Order(
            order_number=order_number,
            customer_name=data.get('customer_name'),
            table_id=table_id,
            table_number_snapshot=table_snapshot, # <-- Disimpan di sini
            order_type=data.get('order_type'),
            payment_method=safe_payment_method,
            payment_status=pay_status,
            order_status='pending',
            total_amount=data.get('total_amount', 0)
        )
        
        db.session.add(new_order)
        db.session.flush() # Ambil ID order sebelum commit untuk digunakan di item

        # 3. Simpan Setiap Item ke OrderItem
        for item in cart:
            menu_asli = db.session.get(Menu, item['id'])
            if not menu_asli:
                db.session.rollback()
                return jsonify({
                    "success": False, 
                    "message": f"Menu '{item['nama']}' sudah tidak tersedia!" 
                })
            harga_valid = menu_asli.price

            # ==========================================
            # LOGIKA PENGURANGAN STOK (Hanya jika stock tidak NULL)
            # ==========================================
            if menu_asli.stock is not None:
                # Pastikan stok cukup sebelum dikurangi (Opsional, untuk keamanan ekstra)
                if menu_asli.stock >= item['qty']:
                    menu_asli.stock -= item['qty']
                else:
                    # Jika stok ternyata tidak cukup (misal dibalap user lain)
                    db.session.rollback()
                    return jsonify({"success": False, "message": f"Stok {menu_asli.name} tidak cukup!"})
            # ==========================================

            order_item = OrderItem(
                order_id=new_order.id,
                menu_id=item['id'],
                qty=item['qty'],
                price_at_order=harga_valid,
                notes=item.get('note', ''),
                item_status='pending'
            )
            db.session.add(order_item)

        db.session.commit()
        return jsonify({
            "success": True, 
            "message": "Pesanan berhasil dibuat!", 
            "order_number": order_number
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})