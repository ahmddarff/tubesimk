import os
from utils import *
from datetime import date, datetime, timedelta, timezone
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from models import Category, Menu, OperationalHour, Reservation, Order, OrderItem, Table, CafeSetting, ReservationTable, User
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

kasir_bp = Blueprint('kasir', __name__)

# ==========================================
# CONTEXT PROCESSOR (GLOBAL VARIABLES UNTUK TEMPLATE)
# ==========================================
@kasir_bp.context_processor
def inject_cafe_setting():
    # Ambil data pengaturan kafe baris pertama
    cafe = CafeSetting.query.first()
    return dict(cafe_setting=cafe)

# =========================
# DASHBOARD
# =========================
@kasir_bp.route('/dashboard')
@login_required
@role_required('kasir')
def dashboard():
    auto_cleanup_expired_orders()
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
    tables_db = Table.query.filter_by(is_available=True).order_by(Table.table_number).all()
    
    # 1. Ambil semua kategori untuk tombol filter
    categories_db = Category.query.order_by(Category.name).all()
    
    menus_db = Menu.query.all()
    menu_list = []
    
    menus_db = Menu.query.all()
    menu_list = []
    
    for m in menus_db:
        if m.is_available and (m.stock is None or m.stock > 0):
            status_menu = 'tersedia'
        else:
            status_menu = 'habis'

        # ── HITUNG REAL RATINGS & TOTAL ULASAN ──
        all_ratings = [oi.review.rating for oi in m.order_items if oi.review]
        
        if all_ratings:
            avg_rating = round(sum(all_ratings) / len(all_ratings), 1)
            total_reviews = len(all_ratings)
        else:
            avg_rating = 0.0
            total_reviews = 0 # Penanda mutlak kalau belum ada ulasan
            
        menu_list.append({
            "id": m.id,
            "nama": m.name,
            "harga": m.price,
            "img": m.image_url if m.image_url else "gambar.png", 
            "status": status_menu,
            "category_id": str(m.category_id),
            "rating": avg_rating,
            "total_reviews": total_reviews  # ✅ SUNTIKKAN VARIABEL INI
        })

    # ==========================================
    # 3. LOGIKA MODE EDIT PESANAN (MENDUKUNG MULTI-MEJA)
    # ==========================================
    edit_order_id = request.args.get('edit')
    edit_data = None

    if edit_order_id:
        order_to_edit = Order.query.filter_by(order_number=edit_order_id).first()
        if order_to_edit:
            # --- PATCH MULTI-MEJA ---
            table_ids_array = []
            if order_to_edit.table_number_snapshot:
                old_table_numbers = [num.strip() for num in order_to_edit.table_number_snapshot.split(',')]
                old_tables_db = Table.query.filter(Table.table_number.in_(old_table_numbers)).all()
                for old_t in old_tables_db:
                    table_ids_array.append(str(old_t.id))
                    if old_t not in tables_db:
                        tables_db.append(old_t)
                tables_db.sort(key=lambda x: str(x.table_number))
            elif order_to_edit.table_id:
                # Fallback jika mengedit data lama yang belum pakai snapshot
                table_ids_array.append(str(order_to_edit.table_id))
                meja_sekarang = db.session.get(Table, order_to_edit.table_id)
                if meja_sekarang and meja_sekarang not in tables_db:
                    tables_db.append(meja_sekarang)
                tables_db.sort(key=lambda x: str(x.table_number))
            # -------------------------
            
            cart_items = []
            for item in order_to_edit.items:
                cart_items.append({
                    "id": item.menu_id,
                    "nama": item.menu.name if item.menu else "Menu Dihapus",
                    "harga": item.price_at_order,
                    "qty": item.qty,
                    "note": item.notes or "",
                    "img": item.menu.image_url if item.menu and item.menu.image_url else "gambar.png",
                    "status": item.item_status
                })
            
            edit_data = {
                "order_number": order_to_edit.order_number,
                "customer_name": order_to_edit.customer_name or (order_to_edit.customer.name if order_to_edit.customer else "Tamu"),
                "table_ids": table_ids_array, # ✅ BARU: Mengirim array meja
                "order_type": "dine-in" if order_to_edit.order_type == "dine_in" else "takeaway",
                "cart": cart_items,
                "lunas": True if order_to_edit.payment_status == 'paid' else False,
                "has_account": True if order_to_edit.user_id is not None else False
            }
    
    # ==========================================
    # 3.5 LOGIKA CHECK-IN RESERVASI KE ORDER (MUTLAK CONFIRMED ONLY)
    # ==========================================
    checkin_res_id = request.args.get('checkin')
    checkin_data = None
    checkin_error = None 

    if checkin_res_id:
        res_to_checkin = db.session.get(Reservation, int(checkin_res_id))
        
        if not res_to_checkin:
            checkin_error = "Reservasi tidak ditemukan di database!"
        # ✅ REVISI: Tolak semua status selain 'confirmed'
        elif res_to_checkin.status != 'confirmed':
            status_indo = {"pending": "Menunggu", "completed": "Selesai", "cancelled": "Dibatalkan"}.get(res_to_checkin.status, res_to_checkin.status)
            checkin_error = f"Akses Ditolak! Reservasi ini berstatus '{status_indo}'. Hanya reservasi yang telah 'Dikonfirmasi' yang boleh melakukan Check-In."
        else:
            table_ids_array = [str(rt.table_id) for rt in res_to_checkin.reserved_tables if rt.table_id]
            
            for rt in res_to_checkin.reserved_tables:
                if rt.table_id:
                    t_obj = db.session.get(Table, rt.table_id)
                    if t_obj and t_obj not in tables_db:
                        tables_db.append(t_obj)
            
            tables_db.sort(key=lambda x: str(x.table_number))
            
            checkin_data = {
                "id": res_to_checkin.id,
                "customer_name": res_to_checkin.customer_name or (res_to_checkin.user.name if res_to_checkin.user else "Tamu"),
                "table_ids": table_ids_array,
                "order_type": "dine-in",
                "is_mandiri": True if res_to_checkin.user_id else False
            }

    # ==========================================
    # 4. DATA RESERVASI HARI INI (Untuk Warning Buffer di Keranjang)
    # ==========================================
    upcoming_res_db = Reservation.query.filter(
        Reservation.reservation_date == today,
        Reservation.status.in_(['pending', 'confirmed'])
    ).all()
    
    upcoming_reservations = []
    for r in upcoming_res_db:
        if r.reservation_time:
            for rt in r.reserved_tables:
                upcoming_reservations.append({
                    "table_id": str(rt.table_id), # Jadikan string agar mudah dicocokkan di JS
                    "time": r.reservation_time.strftime('%H:%M'),
                    "customer": r.customer_name or (r.user.name if r.user else "Tamu"),
                    "duration": r.duration
                })

    # ==========================================
    # 4. RENDER TEMPLATE
    # ==========================================
    return render_template(
        'kasir/dashboard.html', 
        segment='dashboard',
        role='kasir',
        stats=stats_data,
        tables=tables_db,
        categories=categories_db,
        menu=menu_list,
        edit_data=edit_data,
        upcoming_reservations=upcoming_reservations,
        checkin_data=checkin_data,
        checkin_error=checkin_error
    )

# =========================
# PESANAN AKTIF
# =========================
@kasir_bp.route('/pesanan-aktif')
@login_required
@role_required('kasir')
def pesanan_aktif():
    auto_cleanup_expired_orders()
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
    # Syarat B: Statusnya sudah disajikan (served) TAPI belum dibayar (unpaid)
    # Syarat C (BARU): Sudah lunas (paid) & disajikan (served), TAPI meja belum dikosongkan (khusus dine-in)
    orders_db = Order.query.filter(
        Order.payment_status != 'cancelled',
        db.or_(
            Order.order_status.in_(['pending', 'preparing', 'ready']),
            db.and_(Order.order_status == 'served', Order.payment_status == 'unpaid'),
            # ✅ REVISI WORKFLOW: Kunci kartu dine-in agar tidak hilang sebelum kasir lepas meja
            db.and_(
                Order.order_status == 'served', 
                Order.payment_status == 'paid', 
                Order.order_type == 'dine_in', 
                Order.table_id.isnot(None)
            )
        )
    ).order_by(Order.created_at.asc()).all()
    
    pesanan_aktif_data = []
    
    for order in orders_db:
        # Menyiapkan daftar menu per pesanan
        items_list = []
        for item in order.items:
            items_list.append({
                'id': item.id,  # ✅ TAMBAHKAN BARIS INI (Wajib untuk update status per item)
                'nama': item.menu.name if item.menu else 'Item Tidak Dikenal',
                'qty': item.qty,
                'harga': item.price_at_order,
                'catatan': item.notes or '',
                'status': item.item_status
            })

        tipe_map = {'dine_in': 'DINE IN', 'take_away': 'TAKE AWAY'}
        nama_pelanggan = order.customer_name or (order.customer.name if order.customer else "Tamu")

        # AMBIL DATA METODE DARI DB (Ubah jadi huruf besar, default CASH jika kosong)
        pm_raw = order.payment_method
        metode_bayar = str(pm_raw).upper() if pm_raw else 'CASH'

        pesanan_aktif_data.append({
            'id': order.order_number,
            'nama': nama_pelanggan,
            'waktu_iso': order.created_at.isoformat() + 'Z',
            'tipe': tipe_map.get(order.order_type, 'DINE IN'),
            'meja': order.table_number_snapshot or '-',
            'status': str(order.order_status).upper(), 
            'total': order.total_amount,
            'lunas': True if order.payment_status == 'paid' else False,
            'metode': metode_bayar, # <--- TAMBAHAN BARU
            'uang_diterima': order.received_amount,
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
@role_required('kasir')
def reservasi():
    auto_cleanup_expired_reservations()
    reservations_db = Reservation.query.order_by(
        Reservation.reservation_date.desc(),
        Reservation.reservation_time.asc()
    ).all()
    
    all_tables = Table.query.order_by(Table.table_number.asc()).all()
    tables_list = [{"id": t.id, "number": t.table_number, "capacity": t.capacity} for t in all_tables]
    
    data_reservasi = []

    for res in reservations_db:
        nama_pelanggan = res.customer_name or (res.user.name if res.user else "Tanpa Nama")

        meja_list = [rt.table_number_snapshot for rt in res.reserved_tables]
        meja_str = ", ".join(meja_list) if meja_list else "-"
        meja_ids = [rt.table_id for rt in res.reserved_tables if rt.table_id]

        jam_mulai_str = ""
        jam_selesai_str = ""
        if res.reservation_time:
            jam_mulai_str = res.reservation_time.strftime('%H:%M')
            if res.duration:
                mulai_dt = datetime.combine(datetime.today(), res.reservation_time)
                selesai_dt = mulai_dt + timedelta(minutes=res.duration)
                jam_selesai_str = selesai_dt.strftime('%H:%M')

        data_reservasi.append({
            'id': res.id,
            'nomor_reservasi': res.reservation_number,
            'nama': nama_pelanggan,
            'tanggal': res.reservation_date.strftime('%Y-%m-%d') if res.reservation_date else '',
            'tamu': res.guest_qty,
            'telepon': res.phone,
            'jam_mulai': jam_mulai_str,
            'jam_selesai': jam_selesai_str,
            # ✅ PERBAIKAN: Kirim Raw Data (pending/confirmed) langsung ke frontend, HAPUS status_mapping!
            'status': res.status, 
            'meja': meja_str,
            'table_ids': meja_ids,
            'notes': res.notes or '',
            'alasan_batal': res.cancellation_reason or '',
            'is_mandiri': True if res.user_id else False
        })

    return render_template(
        'kasir/reservasi.html',
        segment='reservasi',
        role='kasir',
        reservations=data_reservasi,
        tables=tables_list
    )

# =========================
# RIWAYAT TRANSAKSI
# =========================
@kasir_bp.route('/riwayat-transaksi')
@login_required
@role_required('kasir')
def riwayat_transaksi():
    # PAID & SERVED wajib memiliki table_id NULL (artinya kasir sudah lepas meja)
    orders_db = Order.query.filter(
        db.or_(
            db.and_(Order.payment_status == 'paid', Order.order_status == 'served', Order.table_id.is_(None)),
            Order.payment_status == 'cancelled'
        )
    ).order_by(Order.created_at.desc()).all()
    
    data_transaksi = []
    
    for order in orders_db:
        items_list = []
        for item in order.items:
            items_list.append({
                'nama': item.menu.name if item.menu else 'Item Terhapus',
                'harga': item.price_at_order,
                'jumlah': item.qty,
                'subtotal': item.price_at_order * item.qty,
                'note': item.notes or '' 
            })

        nama_pelanggan = order.customer_name or (order.customer.name if order.customer else "Tamu")
        pm_raw = order.payment_method
        metode_bayar = str(pm_raw).upper() if pm_raw else '-'
        tipe_map = {'dine_in': 'DINE IN', 'take_away': 'TAKE AWAY'}
        nama_kasir = order.cashier.name if order.cashier else 'Self-Service'

        data_transaksi.append({
            'id': order.order_number,
            
            'tanggal': f"{format_tanggal_lokal(order.created_at)}, {format_waktu_lokal(order.created_at)}",
            'tanggal_mentah': format_tanggal_mentah(order.created_at),
            
            'kasir': nama_kasir,
            'pelanggan': nama_pelanggan,
            'metode': metode_bayar,
            'tipe': tipe_map.get(order.order_type, 'DINE IN'),
            'meja': order.table_number_snapshot or '-',
            'status_pembayaran': order.payment_status, 
            'total': order.total_amount,
            'uang_diterima': order.received_amount,
            'alasan_batal': order.cancellation_reason or '', 
            'items': items_list,
            'sumber': 'APLIKASI' if order.user_id else 'KASIR'
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
@role_required('kasir')
def pengaturan():
    if request.method == 'POST':
        nama_baru = request.form.get('name', '').strip()
        username_baru = request.form.get('username', '').strip()
        email_baru = request.form.get('email', '').strip()
        phone_baru = request.form.get('phone', '').strip()

        # ✅ VALIDASI BACKEND BARU
        if not nama_baru or not username_baru:
            return jsonify({"success": False, "message": "Nama dan Username wajib diisi!"})
            
        if " " in username_baru:
            return jsonify({"success": False, "message": "Username tidak boleh mengandung spasi!"})

        # Cek apakah username sudah dipakai orang lain
        if username_baru != current_user.username and User.query.filter_by(username=username_baru).first():
            return jsonify({"success": False, "message": "Username tersebut sudah digunakan orang lain!"})

        # Terapkan perubahan
        current_user.name = nama_baru
        current_user.username = username_baru
        current_user.email = email_baru
        current_user.phone = phone_baru

        # Konsisten menggunakan 'photo'
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                upload_path = os.path.join(current_app.root_path, 'static/uploads/profile')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

                # Hapus foto lama jika ada
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
                
                # Simpan path relatifnya ke database
                current_user.photo = f"uploads/profile/{unique_filename}"

        try:
            db.session.commit()
            return jsonify({"success": True, "message": "Profil berhasil diperbarui!"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": "Gagal memperbarui profil. Email mungkin sudah digunakan."})

    return render_template('kasir/pengaturan.html', segment='pengaturan', role='kasir', user=current_user)

@kasir_bp.route('/api/update-password', methods=['POST'])
@login_required
@role_required('kasir')
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
@role_required('kasir')
def submit_order():
    data = request.json
    cart = data.get('cart', [])
    
    if not cart:
        return jsonify({"success": False, "message": "Keranjang kosong!"})
    
    # ✅ BARIKADE 0: CEK STATUS OPERASIONAL KAFE SAAT INI (REAL-TIME WIB)
    waktu_sekarang = to_wib(datetime.now(timezone.utc))
    jam_sekarang = waktu_sekarang.time()
    
    hari_indo = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}
    nama_hari = hari_indo[waktu_sekarang.weekday()]

    # 1. Cek apakah Owner mematikan operasional kafe secara manual (Tutup Darurat)
    cafe = CafeSetting.query.first()
    if cafe and not cafe.is_open:
        return jsonify({"success": False, "message": "Gagal! Kafe saat ini sedang ditutup secara manual oleh Owner."})

    # 2. Cek Jadwal Harian
    jadwal = OperationalHour.query.filter_by(day_of_week=nama_hari).first()
    if not jadwal or not jadwal.is_open:
        return jsonify({"success": False, "message": f"Transaksi ditolak. Kafe libur/tutup pada hari {nama_hari}."})
        
    if jam_sekarang < jadwal.open_time or jam_sekarang > jadwal.close_time:
        return jsonify({
            "success": False, 
            "message": f"Transaksi ditolak. Saat ini di luar jam operasional {nama_hari} ({jadwal.open_time.strftime('%H:%M')} - {jadwal.close_time.strftime('%H:%M')} WIB)."
        })

    try:
        order_number = generate_order_number()

        payment_method_raw = data.get('payment_method')
        safe_payment_method = payment_method_raw.lower() if payment_method_raw else None
        
        if safe_payment_method in ['qris', 'cash']:
            pay_status = 'paid'
        else:
            pay_status = 'unpaid'

        received_amount_raw = data.get('received_amount')
        safe_received_amount = int(received_amount_raw) if received_amount_raw and str(received_amount_raw).isdigit() else data.get('total_amount', 0)

        # ==========================================
        # REVISI: LOGIKA MULTI-MEJA (Master Table + Snapshot)
        # ==========================================
        order_type = data.get('order_type')
        table_ids = data.get('table_ids', []) # Menerima Array ID Meja
        
        primary_table_id = None
        table_snapshot_str = None

        if order_type == 'dine_in' and table_ids:
            primary_table_id = table_ids[0] # Jadikan meja pertama sebagai Master (Gembok Relasi)
            snapshot_list = []
            
            # Looping untuk mengunci semua meja fisik yang dipilih kasir
            for t_id in table_ids:
                table_obj = db.session.get(Table, int(t_id))
                if table_obj:
                    table_obj.is_available = False # Kunci meja!
                    snapshot_list.append(table_obj.table_number)
            
            # Gabungkan nomor meja menjadi string (contoh: "01, 02, 03")
            if snapshot_list:
                table_snapshot_str = ", ".join(snapshot_list)
        # ==========================================

        new_order = Order(
            order_number=order_number,
            customer_name=data.get('customer_name'),
            table_id=primary_table_id,             # <-- Master Table ID
            table_number_snapshot=table_snapshot_str, # <-- String Gabungan
            order_type=order_type,
            payment_method=safe_payment_method,
            payment_status=pay_status,
            order_status='pending',
            total_amount=data.get('total_amount', 0),
            received_amount=safe_received_amount if pay_status == 'paid' else None,
            cashier_id=current_user.id,
        )
        
        db.session.add(new_order)
        db.session.flush()

        for item in cart:
            menu_asli = db.session.get(Menu, item['id'])
            if not menu_asli:
                db.session.rollback()
                return jsonify({"success": False, "message": f"Menu '{item['nama']}' sudah tidak tersedia!"})
            
            harga_valid = menu_asli.price

            if menu_asli.stock is not None:
                if menu_asli.stock >= item['qty']:
                    menu_asli.stock -= item['qty']
                else:
                    db.session.rollback()
                    return jsonify({"success": False, "message": f"Stok {menu_asli.name} tidak cukup!"})

            order_item = OrderItem(
                order_id=new_order.id,
                menu_id=item['id'],
                qty=item['qty'],
                price_at_order=harga_valid,
                notes=item.get('note', ''),
                item_status='pending'
            )
            db.session.add(order_item)

        checkin_res_id = data.get('checkin_reservation_id')
        if checkin_res_id:
            res_obj = db.session.get(Reservation, int(checkin_res_id))
            if res_obj:
                res_obj.status = 'completed'

        db.session.commit()
        return jsonify({
            "success": True, 
            "message": "Pesanan berhasil dibuat!", 
            "order_number": order_number
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})


@kasir_bp.route('/api/update-order', methods=['POST'])
@login_required
@role_required('kasir')
def update_order():
    data = request.json
    order_number = data.get('order_number')
    cart = data.get('cart', [])
    
    if not order_number:
        return jsonify({"success": False, "message": "Nomor pesanan tidak valid!"})
        
    try:
        order = Order.query.filter_by(order_number=order_number).first()
        if not order:
            return jsonify({"success": False, "message": "Pesanan tidak ditemukan!"})
            
        if order.payment_status == 'paid':
            return jsonify({"success": False, "message": "Pesanan yang sudah lunas tidak dapat diubah!"})
            
        # ==========================================
        # REVISI: UPDATE MEJA LAMA KE MEJA BARU (Multi-Meja)
        # ==========================================
        new_order_type = data.get('order_type')
        new_table_ids = data.get('table_ids', []) # Array meja baru dari Frontend
        
        # 1. LEPASKAN SEMUA MEJA LAMA TERLEBIH DAHULU
        if order.table_number_snapshot:
            # Pecah string "01, 02" menjadi array
            old_table_numbers = [num.strip() for num in order.table_number_snapshot.split(',')]
            old_tables_db = Table.query.filter(Table.table_number.in_(old_table_numbers)).all()
            for old_t in old_tables_db:
                old_t.is_available = True # Bebaskan meja lama
        
        # 2. TEMPATI & KUNCI MEJA BARU
        primary_table_id = None
        table_snapshot_str = None

        if new_order_type == 'dine_in' and new_table_ids:
            primary_table_id = new_table_ids[0]
            snapshot_list = []
            for t_id in new_table_ids:
                new_t = db.session.get(Table, int(t_id))
                if new_t:
                    new_t.is_available = False # Kunci meja baru
                    snapshot_list.append(new_t.table_number)
            
            if snapshot_list:
                table_snapshot_str = ", ".join(snapshot_list)
        
        order.table_id = primary_table_id
        order.table_number_snapshot = table_snapshot_str
        # ==========================================
            
        order.customer_name = data.get('customer_name')
        order.order_type = new_order_type
        order.total_amount = data.get('total_amount', 0)
        order.cashier_id = current_user.id

        payment_method_raw = data.get('payment_method')
        if payment_method_raw: 
            safe_pm = payment_method_raw.lower()
            order.payment_method = safe_pm
            order.payment_status = 'paid'
        
        # SINKRONISASI DAFTAR MENU
        pending_items = OrderItem.query.filter_by(order_id=order.id, item_status='pending').all()
        for p_item in pending_items:
            if p_item.menu and p_item.menu.stock is not None:
                p_item.menu.stock += p_item.qty
            db.session.delete(p_item)
        
        for item in cart:
            status_item = item.get('status')
            if status_item in ['preparing', 'ready', 'served']:
                continue
                
            menu_asli = db.session.get(Menu, item['id'])
            if not menu_asli:
                db.session.rollback()
                return jsonify({"success": False, "message": f"Menu '{item['nama']}' tidak ditemukan!"})
                
            if menu_asli.stock is not None:
                if menu_asli.stock < item['qty']:
                    db.session.rollback()
                    return jsonify({"success": False, "message": f"Stok untuk '{menu_asli.name}' tidak mencukupi!"})
                menu_asli.stock -= item['qty']
                
            new_order_item = OrderItem(
                order_id=order.id,
                menu_id=item['id'],
                qty=item['qty'],
                price_at_order=menu_asli.price,
                notes=item.get('note', ''),
                item_status='pending'
            )
            db.session.add(new_order_item)
            
        db.session.commit()
        return jsonify({"success": True, "message": "Pesanan berhasil diperbarui!"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})
    
# ── Pesanan Aktif APIs ─────────────────────────────────────────
@kasir_bp.route('/api/cancel-order', methods=['POST'])
@login_required
@role_required('kasir')
def cancel_order():
    data = request.json
    order_id = data.get('order_id')
    alasan = data.get('alasan', 'Dibatalkan oleh kasir') # Menangkap alasan batal jika ada

    if not order_id:
        return jsonify({"success": False, "message": "ID Pesanan tidak valid!"})

    try:
        order = Order.query.filter_by(order_number=order_id).first()
        
        if not order:
            return jsonify({"success": False, "message": "Pesanan tidak ditemukan!"})

        if order.payment_status == 'paid':
            return jsonify({"success": False, "message": "Pesanan lunas tidak dapat dibatalkan!"})

        # 1. UBAH STATUS MENJADI CANCELLED
        order.payment_status = 'cancelled'
        order.cancellation_reason = alasan

        order.cashier_id = current_user.id  # catat kasir yg membatalkan utk histori

        # 2. LEPASKAN MEJA (Jika pesanan Dine-In dan sedang menempati meja)
        if order.table_id:
            table = db.session.get(Table, order.table_id)
            if table:
                table.is_available = True
            # Jangan hapus table_number_snapshot agar histori tetap tahu pesanan ini dulu di meja berapa
            order.table_id = None 

        # 3. KEMBALIKAN STOK FISIK (Hanya untuk item yang belum dimasak / pending)
        for item in order.items:
            if item.item_status == 'pending' and item.menu and item.menu.stock is not None:
                item.menu.stock += item.qty

        db.session.commit()
        return jsonify({"success": True, "message": f"Pesanan {order_id} berhasil dibatalkan."})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@kasir_bp.route('/api/pay-order', methods=['POST'])
@login_required
@role_required('kasir')
def pay_order():
    data = request.json
    order_number = data.get('order_number')
    payment_method = data.get('payment_method')
    received_amount = data.get('received_amount')
    
    if not order_number or not payment_method:
        return jsonify({"success": False, "message": "Data pembayaran tidak lengkap!"})
        
    try:
        order = Order.query.filter_by(order_number=order_number).first()
        if not order:
            return jsonify({"success": False, "message": "Pesanan tidak ditemukan!"})
            
        if order.payment_status == 'paid':
            return jsonify({"success": False, "message": "Pesanan ini sudah lunas sebelumnya!"})
            
        # Proses pelunasan dan catat metodenya
        order.payment_status = 'paid'
        order.payment_method = payment_method.upper() if payment_method.upper() in ['CASH', 'QRIS'] else 'CASH'
        order.received_amount = int(received_amount) if received_amount and str(received_amount).isdigit() else order.total_amount

        order.cashier_id = current_user.id  # catat kasir yg menerima pembayaran utk histori
        
        db.session.commit()
        return jsonify({"success": True, "message": "Pembayaran berhasil!"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@kasir_bp.route('/api/release-table', methods=['POST'])
@login_required
@role_required('kasir')
def release_table():
    data = request.json
    order_number = data.get('order_number')
    
    if not order_number:
        return jsonify({"success": False, "message": "Nomor pesanan tidak valid!"})
        
    try:
        order = Order.query.filter_by(order_number=order_number).first()
        if not order:
            return jsonify({"success": False, "message": "Pesanan tidak ditemukan!"})
            
        # 1. 🔓 BEBASKAN MULTI-MEJA menggunakan snapshot string secara massal
        if order.table_number_snapshot:
            table_numbers = [num.strip() for num in order.table_number_snapshot.split(',')]
            tables_to_release = Table.query.filter(Table.table_number.in_(table_numbers)).all()
            for table in tables_to_release:
                table.is_available = True  # Kembalikan status meja fisik menjadi TERSEDIA
        
        # Lepaskan gembok id relasi master agar tidak membingungkan sistem CCTV dashboard
        order.table_id = None
        
        # 2. Paksa status pesanan utama menjadi SERVED agar bersih dari grid Pesanan Aktif
        order.order_status = 'served'
        
        db.session.commit()
        return jsonify({"success": True, "message": f"Meja untuk pesanan {order_number} sukses dikosongkan!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@kasir_bp.route('/api/complete-takeaway', methods=['POST'])
@login_required
@role_required('kasir')
def complete_takeaway():
    data = request.json
    order_number = data.get('order_number')
    
    if not order_number:
        return jsonify({"success": False, "message": "Nomor pesanan tidak valid!"})
        
    try:
        order = Order.query.filter_by(order_number=order_number).first()
        if not order:
            return jsonify({"success": False, "message": "Pesanan tidak ditemukan!"})
            
        # 1. Ubah status pesanan induk langsung menjadi SERVED
        order.order_status = 'served'
        
        # 2. Paksa ubah semua status item di dalamnya menjadi SERVED sekaligus
        for item in order.items:
            item.item_status = 'served'
            
        db.session.commit()
        return jsonify({"success": True, "message": f"Pesanan Take Away {order_number} berhasil diselesaikan!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})
    
@kasir_bp.route('/api/serve-item', methods=['POST'])
@login_required
@role_required('kasir')
def serve_item():
    data = request.json
    item_id = data.get('item_id')
    
    if not item_id:
        return jsonify({"success": False, "message": "ID Item tidak valid!"})
        
    try:
        item = db.session.get(OrderItem, int(item_id))
        if not item:
            return jsonify({"success": False, "message": "Item tidak ditemukan!"})
            
        # 1. Ubah status item spesifik ini menjadi 'served'
        item.item_status = 'served'
        
        # 2. 🚀 PANGGIL FUNGSI SINKRONISASI DARI utils.py
        auto_sync_order_status(item.order)
        
        db.session.commit()
        
        # Kembalikan status induk terbaru (kapital) agar UI langsung menyesuaikan
        return jsonify({
            "success": True, 
            "message": f"{item.menu.name} berhasil diantar!",
            "new_order_status": item.order.order_status.upper()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})
    
# ── Reservasi APIs ─────────────────────────────────────────
@kasir_bp.route('/api/add-reservation', methods=['POST'])
@login_required
@role_required('kasir')
def add_reservation():
    data = request.json
    try:
        res_date = datetime.strptime(data.get('tanggal'), '%Y-%m-%d').date()
        res_time = datetime.strptime(data.get('jam_mulai'), '%H:%M').time()
        duration = int(data.get('durasi', 90))
        tamu_qty = int(data.get('tamu', 1))
        table_ids = data.get('table_ids', [])

        if duration <= 0 or tamu_qty <= 0:
            return jsonify({"success": False, "message": "Durasi dan jumlah tamu harus lebih dari 0!"})
            
        new_start = datetime.combine(res_date, res_time)
        new_end = new_start + timedelta(minutes=duration)
        
        new_start = datetime.combine(res_date, res_time)
        new_end = new_start + timedelta(minutes=duration)

        # ✅ BARIKADE 0: CEK JAM OPERASIONAL KAFE
        hari_indo = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}
        nama_hari = hari_indo[res_date.weekday()] # Dapatkan nama hari dari tanggal
        
        jadwal = OperationalHour.query.filter_by(day_of_week=nama_hari).first()
        
        if not jadwal:
            return jsonify({"success": False, "message": f"Jadwal operasional untuk hari {nama_hari} belum diatur oleh Owner."})
            
        if not jadwal.is_open:
            return jsonify({"success": False, "message": f"Maaf, kafe TUTUP pada hari {nama_hari}."})
            
        # Cek apakah jam mulai kurang dari jam buka, ATAU jam selesai melebihi jam tutup
        if res_time < jadwal.open_time or new_end.time() > jadwal.close_time:
            return jsonify({
                "success": False, 
                "message": f"Waktu reservasi di luar jam operasional {nama_hari} ({jadwal.open_time.strftime('%H:%M')} - {jadwal.close_time.strftime('%H:%M')})."
            })
        
        # ── BARIKADE 1: CEK APAKAH WAKTU SUDAH TERLEWAT ──
        if new_start < datetime.now():
            return jsonify({"success": False, "message": "Gagal! Tidak dapat membuat reservasi untuk waktu yang sudah terlewat."})
        
        # Tarik Pengaturan Kafe dari Database
        cafe_setting = CafeSetting.query.first()
        clearance_mins = cafe_setting.table_clearance_time if cafe_setting else 15
        clearance_delta = timedelta(minutes=clearance_mins)
        buffer_mins = cafe_setting.reservation_buffer_time if cafe_setting else 90
        
        # ── BARIKADE 2: CEK KONDISI FISIK MEJA SAAT INI (Rolling Buffer) ──
        if res_date == date.today():
            now_dt = datetime.now()
            
            for t_id in table_ids:
                # Ambil data meja langsung dari database
                table_obj = db.session.get(Table, int(t_id))
                
                # ✅ JAUH LEBIH AMAN: Jika fisik meja terisi (is_available == False), 
                # tidak peduli dia belum bayar atau sudah lunas tapi masih nongkrong!
                if table_obj and not table_obj.is_available:
                    walk_in_end = now_dt + timedelta(minutes=buffer_mins)
                    total_wait_end = walk_in_end + clearance_delta
                    
                    if new_start < total_wait_end:
                        return jsonify({
                            "success": False, 
                            "message": f"Meja {table_obj.table_number} saat ini secara fisik MASIH TERISI di tempat. Meja diperkirakan baru siap bersih paling cepat pukul {total_wait_end.strftime('%H:%M')} (Dihitung dari waktu sekarang)."
                        })
        
        # ── BARIKADE 3: CEK BENTROK JADWAL RESERVASI LAIN ──
        existing_res = Reservation.query.filter(
            Reservation.reservation_date == res_date,
            Reservation.status.in_(['pending', 'confirmed', 'completed'])
        ).all()
        
        for res in existing_res:
            ex_start = datetime.combine(res.reservation_date, res.reservation_time)
            ex_end = ex_start + timedelta(minutes=res.duration)
            
            if (new_start < ex_end + clearance_delta) and (new_end > ex_start - clearance_delta):
                for rt in res.reserved_tables:
                    if str(rt.table_id) in [str(tid) for tid in table_ids]:
                        return jsonify({
                            "success": False, 
                            "message": f"Meja {rt.table_number_snapshot} sudah dipesan oleh pelanggan lain pada pukul {ex_start.strftime('%H:%M')} - {ex_end.strftime('%H:%M')} (Termasuk jeda pembersihan meja {clearance_mins} menit)."
                        })
                        
        # JIKA LOLOS SEMUA BARIKADE, SIMPAN RESERVASI
        new_res = Reservation(
            reservation_number=generate_reservation_number(),
            customer_name=data.get('nama'),
            phone=data.get('telepon'),
            guest_qty=tamu_qty,
            duration=duration,
            reservation_date=res_date,
            reservation_time=res_time,
            notes=data.get('notes'),
            status=data.get('status', 'pending') 
        )
        db.session.add(new_res)
        db.session.flush()
        
        for t_id in table_ids:
            table_db = db.session.get(Table, int(t_id))
            if table_db:
                res_table = ReservationTable(
                    reservation_id=new_res.id,
                    table_id=table_db.id,
                    table_number_snapshot=table_db.table_number
                )
                db.session.add(res_table)
                
        db.session.commit()
        return jsonify({"success": True, "message": "Reservasi baru berhasil disimpan!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@kasir_bp.route('/api/update-reservation', methods=['POST'])
@login_required
@role_required('kasir')
def update_reservation():
    data = request.json
    res_id = data.get('id')
    try:
        reservation = db.session.get(Reservation, int(res_id))
        if not reservation:
            return jsonify({"success": False, "message": "Reservasi tidak ditemukan!"})

        if reservation.status in ['completed', 'cancelled']:
            return jsonify({"success": False, "message": "Reservasi yang sudah final/batal tidak dapat diubah lagi!"})
            
        res_date = datetime.strptime(data.get('tanggal'), '%Y-%m-%d').date()
        res_time = datetime.strptime(data.get('jam_mulai'), '%H:%M').time()
        duration = int(data.get('durasi', 90))
        tamu_qty = int(data.get('tamu', 1))
        table_ids = data.get('table_ids', [])

        if duration <= 0 or tamu_qty <= 0:
            return jsonify({"success": False, "message": "Durasi dan jumlah tamu harus lebih dari 0!"})
        
        new_status = data.get('status', 'pending')
        
        if new_status != 'cancelled':
            new_start = datetime.combine(res_date, res_time)
            new_end = new_start + timedelta(minutes=duration)

            hari_indo = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}
            nama_hari = hari_indo[res_date.weekday()]
            jadwal = OperationalHour.query.filter_by(day_of_week=nama_hari).first()
            
            if not jadwal or not jadwal.is_open:
                return jsonify({"success": False, "message": f"Maaf, kafe TUTUP pada hari {nama_hari}."})
                
            if res_time < jadwal.open_time or new_end.time() > jadwal.close_time:
                return jsonify({
                    "success": False, 
                    "message": f"Waktu reservasi di luar jam operasional {nama_hari} ({jadwal.open_time.strftime('%H:%M')} - {jadwal.close_time.strftime('%H:%M')})."
                })
            
            cafe_setting = CafeSetting.query.first()
            clearance_mins = cafe_setting.table_clearance_time if cafe_setting else 15
            clearance_delta = timedelta(minutes=clearance_mins)
            
            existing_res = Reservation.query.filter(
                Reservation.reservation_date == res_date,
                Reservation.status.in_(['pending', 'confirmed', 'completed']),
                Reservation.id != reservation.id
            ).all()
            
            for res in existing_res:
                ex_start = datetime.combine(res.reservation_date, res.reservation_time)
                ex_end = ex_start + timedelta(minutes=res.duration)
                
                if (new_start < ex_end + clearance_delta) and (new_end > ex_start - clearance_delta):
                    for rt in res.reserved_tables:
                        if str(rt.table_id) in [str(tid) for tid in table_ids]:
                            return jsonify({
                                "success": False, 
                                "message": f"Bentrok! Meja {rt.table_number_snapshot} sudah dipakai tamu lain dari pukul {ex_start.strftime('%H:%M')} - {ex_end.strftime('%H:%M')}."
                            })
        
        reservation.customer_name = data.get('nama')
        reservation.phone = data.get('telepon')
        reservation.guest_qty = tamu_qty
        reservation.duration = duration
        reservation.reservation_date = res_date
        reservation.reservation_time = res_time
        reservation.notes = data.get('notes')
        reservation.status = new_status # ✅ Simpan ke DB
        
        if new_status == 'cancelled':
            reservation.cancellation_reason = data.get('alasan_batal')
        else:
            reservation.cancellation_reason = None
        
        for old_table in reservation.reserved_tables:
            db.session.delete(old_table)
            
        for t_id in table_ids:
            table_db = db.session.get(Table, int(t_id))
            if table_db:
                res_table = ReservationTable(
                    reservation_id=reservation.id,
                    table_id=table_db.id,
                    table_number_snapshot=table_db.table_number
                )
                db.session.add(res_table)
                
        db.session.commit()
        return jsonify({"success": True, "message": "Perubahan reservasi berhasil disimpan!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})
    

# ==========================================
# INTERNAL HELPER: LAZY CLEANUP ORDER MANDIRI KEDALUWARSA (5 MENIT)
# ==========================================
def auto_cleanup_expired_orders():
    # ✅ FIX FATAL BUG: Gunakan utcnow() agar sejajar apple-to-apple dengan data di DB!
    threshold_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    
    # Cari order mandiri (user_id TIDAK NULL) yang belum bayar, masih pending, & lewat 5 menit
    expired_orders = Order.query.filter(
        Order.user_id.isnot(None),  # Sesuai info kamu: penanda mutlak order mandiri
        Order.payment_status == 'unpaid',
        Order.order_status == 'pending',
        Order.created_at <= threshold_time
    ).all()
    
    for order in expired_orders:
        # 1. Ubah status menjadi batal
        order.payment_status = 'cancelled'
        order.cancellation_reason = 'Dibatalkan otomatis oleh sistem (Batas waktu pembayaran 5 menit habis)'
        
        # 2. 🔓 BEBASKAN MULTI-MEJA menggunakan snapshot string
        if order.table_number_snapshot:
            # Pecah string "01, 02" menjadi array nomor meja
            table_numbers = [num.strip() for num in order.table_number_snapshot.split(',')]
            tables_to_release = Table.query.filter(Table.table_number.in_(table_numbers)).all()
            for table in tables_to_release:
                table.is_available = True # Kembalikan meja fisik menjadi kosong
        
        order.table_id = None # Bersihkan master gembok relasi
        
        # 3. 📦 RESTORASI STOK MENU (Agar stok menu berharga tidak hangus sia-sia)
        for item in order.items:
            if item.item_status == 'pending' and item.menu and item.menu.stock is not None:
                item.menu.stock += item.qty
                
    # Jika ada data yang dibersihkan, lakukan commit massal sekaligus
    if expired_orders:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()

# ==========================================
# INTERNAL HELPER: LAZY CLEANUP RESERVASI KEDALUWARSA (NO-SHOW)
# ==========================================
def auto_cleanup_expired_reservations():
    # ✅ REVISI TERBAIK: Memanfaatkan to_wib() dari utils agar satu pimpinan!
    # datetime.now(timezone.utc) menghasilkan waktu UTC aware saat ini, lalu dikonversi ke WIB
    hari_ini_wib = to_wib(datetime.now(timezone.utc)).date()
    
    # Cari reservasi yang tanggalnya sudah lewat (kemarin atau sebelumnya)
    # dan statusnya masih menggantung (belum selesai / belum batal)
    expired_res = Reservation.query.filter(
        Reservation.reservation_date < hari_ini_wib,
        Reservation.status.in_(['pending', 'confirmed'])
    ).all()
    
    for res in expired_res:
        # Ubah status menjadi batal secara otomatis
        res.status = 'cancelled'
        res.cancellation_reason = 'Dibatalkan otomatis oleh sistem (No-Show: Tanggal kedatangan telah terlewat dan pelanggan tidak hadir)'
        
    # Jika ada data yang dibersihkan, lakukan commit
    if expired_res:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()