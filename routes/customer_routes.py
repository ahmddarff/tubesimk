import os
from utils import *
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash, current_app, abort
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from utils import format_tanggal_lokal, format_waktu_lokal
from models import User, Menu, Category, Order, OrderItem, Table, Reservation, ReservationTable, Review, OperationalHour
from extensions import db

customer_bp = Blueprint('customer', __name__)

# =========================
# BERANDA & MENU
# =========================

# Halaman Beranda: Menampilkan 4 Menu Terlaris dengan Rating Rata-rata
@customer_bp.route('/')
def beranda():
    # 1. Mengambil data semua menu
    all_menus = Menu.query.all()
    
    # 2. Menghitung total penjualan (qty) dan rating untuk setiap menu
    for menu in all_menus:
        # Hitung terjual
        terjual = db.session.query(func.sum(OrderItem.qty))\
            .join(Order, OrderItem.order_id == Order.id)\
            .filter(OrderItem.menu_id == menu.id, Order.payment_status == 'paid')\
            .scalar() or 0
            
        # Hitung rata-rata rating
        reviews = db.session.query(Review.rating)\
            .join(OrderItem, Review.order_item_id == OrderItem.id)\
            .filter(OrderItem.menu_id == menu.id)\
            .all()
            
        avg_rating = 0.0
        if reviews:
            total_rating = sum([r[0] for r in reviews])
            avg_rating = round(total_rating / len(reviews), 1)
            
        # Menambahkan atribut dinamis ke objek menu
        setattr(menu, 'terjual', int(terjual))
        setattr(menu, 'rating_avg', avg_rating)
        
    # 3. Mengurutkan menu berdasarkan jumlah terjual (terbanyak ke sedikit) 
    # dan mengambil 4 menu teratas.
    best_sellers = sorted(all_menus, key=lambda m: m.terjual, reverse=True)[:4]

    return render_template('customer/beranda.html', 
                           best_sellers=best_sellers, 
                           segment='customer', 
                           role='customer')
                           
# Halaman Daftar Menu: Menampilkan semua menu beserta kategori, total terjual, dan rating rata-rata
@customer_bp.route('/daftar-menu')
def daftar_menu():
    categories = Category.query.all()
    menus = Menu.query.all()
    
    menu_data = []
    for menu in menus:
        # 1. Hitung total terjual dari OrderItem (hanya untuk pesanan yang sudah dibayar)
        terjual = db.session.query(func.sum(OrderItem.qty))\
            .join(Order, OrderItem.order_id == Order.id)\
            .filter(OrderItem.menu_id == menu.id, Order.payment_status == 'paid')\
            .scalar() or 0
            
        # 2. Hitung rata-rata rating dari tabel Review berdasarkan menu_id
        reviews = db.session.query(Review.rating)\
            .join(OrderItem, Review.order_item_id == OrderItem.id)\
            .filter(OrderItem.menu_id == menu.id)\
            .all()
            
        avg_rating = 0.0
        if reviews:
            total_rating = sum([r[0] for r in reviews])
            avg_rating = round(total_rating / len(reviews), 1)
            
        # Sisipkan data kalkulasi ke dalam objek menu
        setattr(menu, 'terjual', int(terjual))
        setattr(menu, 'rating_avg', avg_rating)
        
        menu_data.append(menu)
        
    return render_template('customer/daftar_menu.html', 
                           categories=categories, 
                           menu=menu_data, 
                           segment='daftar_menu', 
                           role='customer')

# Halaman Detail Menu: Menampilkan detail menu beserta ulasan pelanggan
@customer_bp.route('/menu/<int:menu_id>')
def menu_detail(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    order_items = OrderItem.query.filter_by(menu_id=menu.id).all()
    
    reviews = []
    total_rating = 0
    
    for item in order_items:
        if item.review:
            nama_pelanggan = "Pelanggan Anonim"
            nama_asli = "Pelanggan Anonim"  
            foto_pelanggan = None
            
            # PERBAIKAN: Ambil data user secara eksplisit menggunakan user_id
            pemesan = User.query.get(item.order.user_id) if item.order.user_id else None
            
            if pemesan:
                nama_asli = pemesan.name
                if current_user.is_authenticated and pemesan.id == current_user.id:
                    nama_pelanggan = "Anda"
                else:
                    nama_pelanggan = pemesan.name
                foto_pelanggan = pemesan.photo
            elif item.order.customer_name:
                nama_asli = item.order.customer_name
                nama_pelanggan = item.order.customer_name
                
            reviews.append({
                'nama': nama_pelanggan,
                'inisial': nama_asli[:2].upper(),  
                'photo': foto_pelanggan,
                'date': item.review.created_at.strftime('%d %b %Y'),
                'rating': item.review.rating,
                'text': item.review.comment
            })
            total_rating += item.review.rating
            
    review_count = len(reviews)
    avg_rating = round(total_rating / review_count, 1) if review_count > 0 else 0
    
    return render_template('customer/menu_detail.html', 
                           menu=menu,
                           reviews=reviews,
                           avg_rating=avg_rating,
                           review_count=review_count,
                           segment='daftar_menu', 
                           role='customer')

# Halaman Ulasan Menu: Menampilkan semua ulasan untuk menu tertentu
@customer_bp.route('/menu/<int:menu_id>/ulasan')
def menu_reviews(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    order_items = OrderItem.query.filter_by(menu_id=menu.id).all()
    
    reviews = []
    total_rating = 0
    
    for item in order_items:
        if item.review:
            nama_pelanggan = "Pelanggan Anonim"
            nama_asli = "Pelanggan Anonim"  
            foto_pelanggan = None
            
            # PERBAIKAN: Ambil data user secara eksplisit menggunakan user_id
            pemesan = User.query.get(item.order.user_id) if item.order.user_id else None
            
            if pemesan:
                nama_asli = pemesan.name
                if current_user.is_authenticated and pemesan.id == current_user.id:
                    nama_pelanggan = "Anda"
                else:
                    nama_pelanggan = pemesan.name
                foto_pelanggan = pemesan.photo
            elif item.order.customer_name:
                nama_asli = item.order.customer_name
                nama_pelanggan = item.order.customer_name
                
            reviews.append({
                'nama': nama_pelanggan,
                'inisial': nama_asli[:2].upper(),  
                'photo': foto_pelanggan,
                'date': item.review.created_at.strftime('%d %b %Y'),
                'rating': item.review.rating,
                'text': item.review.comment
            })
            total_rating += item.review.rating
            
    review_count = len(reviews)
    avg_rating = round(total_rating / review_count, 1) if review_count > 0 else 0
    
    return render_template('customer/menu_reviews.html', 
                           menu=menu,
                           reviews=reviews,
                           avg_rating=avg_rating,
                           review_count=review_count,
                           segment='daftar_menu', 
                           role='customer')

# =========================
# FUNGSI HELPER
# =========================

# Fungsi untuk mengambil keranjang/pesanan aktif milik pengguna
def get_active_cart(user_id, load_relations=False):
    """Mengambil keranjang/pesanan aktif milik pengguna."""
    query = Order.query
    if load_relations:
        from sqlalchemy.orm import joinedload 
        query = query.options(joinedload(Order.items).joinedload(OrderItem.menu))
    
    return query.filter(
        Order.user_id == user_id,
        Order.order_status == 'pending',
        Order.payment_status == 'unpaid',
        Order.payment_method.is_(None) # Hanya ambil jika belum ada metode pembayaran
    ).first()

# Fungsi untuk menghitung ulang total harga keranjang setelah update item
def recalculate_total(order):
    """Menghitung ulang dan memperbarui total harga keranjang."""
    total = sum(i.qty * i.price_at_order for i in order.items)
    order.total_amount = total
    return total

# Fungsi untuk menghitung total terjual dan rata-rata rating untuk sebuah menu
def calculate_menu_stats(menu):
    """Menghitung total terjual dan rata-rata rating untuk sebuah menu."""
    terjual = db.session.query(func.sum(OrderItem.qty))\
        .join(Order, OrderItem.order_id == Order.id)\
        .filter(OrderItem.menu_id == menu.id, Order.payment_status == 'paid')\
        .scalar() or 0
        
    reviews = db.session.query(Review.rating)\
        .join(OrderItem, Review.order_item_id == OrderItem.id)\
        .filter(OrderItem.menu_id == menu.id)\
        .all()
        
    avg_rating = 0.0
    if reviews:
        total_rating = sum([r[0] for r in reviews])
        avg_rating = round(total_rating / len(reviews), 1)
        
    setattr(menu, 'terjual', int(terjual))
    setattr(menu, 'rating_avg', avg_rating)
    return menu

# =========================
# RESERVASI
# =========================

# Halaman List Reservasi Aktif & Riwayat
@customer_bp.route('/buat-reservasi')
@login_required
@role_required('customer')
def buat_reservasi():
    user_reservations = Reservation.query.options(
        joinedload(Reservation.reserved_tables).joinedload(ReservationTable.table_ref)
    ).filter_by(user_id=current_user.id)\
     .order_by(Reservation.reservation_date.desc(), Reservation.reservation_time.desc()).all()
    
    active_reservations = [r for r in user_reservations if r.status in ['pending', 'confirmed']]
    history_reservations = [r for r in user_reservations if r.status in ['completed', 'cancelled']]
    
    return render_template('customer/buat_reservasi.html', 
                           segment='buat_reservasi', 
                           role='customer', 
                           active_reservations=active_reservations, 
                           history_reservations=history_reservations)

# Halaman Form Reservasi Baru (Mengirim daftar meja dari DB)
@customer_bp.route('/reservasi/new')
@login_required
@role_required('customer')
def reservasi_new():
    # Mengambil semua data meja yang berstatus tersedia
    tables = Table.query.filter_by(is_available=True).all()

    # TAMBAHAN: Mengambil data jam operasional dari database
    op_hours = OperationalHour.query.all()
    op_hours_dict = {}
    for oh in op_hours:
        # Menyimpan ke dictionary dengan nama hari (huruf kecil) sebagai key
        op_hours_dict[oh.day_of_week.lower()] = {
            'is_open': oh.is_open,
            'open_time': oh.open_time.strftime('%H:%M') if oh.open_time else None,
            'close_time': oh.close_time.strftime('%H:%M') if oh.close_time else None
        }
        
    return render_template('customer/buat_reservasi_new.html', 
                           segment='buat_reservasi', 
                           role='customer',
                           tables=tables,
                           op_hours=op_hours_dict)

# API Endpoint POST: Menerima data JSON dari Submit Alpine.js
@customer_bp.route('/buat-reservasi/submit', methods=['POST'])
@login_required
@role_required('customer')
def submit_buat_reservasi():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "Data kosong"}), 400

        # Mengambil data dari payload JSON yang baru
        meja_ids = data.get('meja_ids', []) # Sekarang berupa array (list)
        tanggal_str = data.get('tanggal')
        waktu_str = data.get('waktu')
        durasi = data.get('durasi', 120)
        jumlah_tamu = data.get('jumlahTamu')
        telepon = data.get('telepon')
        notes = data.get('notes', '')

        # Validasi wajib isi
        if not all([meja_ids, tanggal_str, waktu_str, jumlah_tamu, telepon]):
            return jsonify({"success": False, "message": "Mohon lengkapi semua data utama yang diwajibkan!"}), 400

        # Parsing Date dan Time objek
        reservation_date = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
        reservation_time = datetime.strptime(waktu_str, '%H:%M').time()

        # === TAMBAHAN: VALIDASI JAM OPERASIONAL ===
        hari_map = {0: 'senin', 1: 'selasa', 2: 'rabu', 3: 'kamis', 4: 'jumat', 5: 'sabtu', 6: 'minggu'}
        nama_hari = hari_map[reservation_date.weekday()]
        
        op_hour = OperationalHour.query.filter(func.lower(OperationalHour.day_of_week) == nama_hari).first()
        
        # 1. Validasi jika kafe tutup di hari tersebut
        if not op_hour or not op_hour.is_open:
            return jsonify({"success": False, "message": f"Maaf, kafe tutup pada hari {nama_hari.capitalize()}."}), 400
            
        # 2. Validasi jika jam mulai reservasi di luar jam operasional
        if reservation_time < op_hour.open_time or reservation_time > op_hour.close_time:
            return jsonify({"success": False, "message": f"Jam reservasi di luar jam operasional ({op_hour.open_time.strftime('%H:%M')} - {op_hour.close_time.strftime('%H:%M')})."}), 400

        reservation_number = generate_reservation_number()

        # 1. Simpan data induk ke tabel 'reservations'
        new_reservation = Reservation(
            reservation_number=reservation_number,
            user_id=current_user.id,
            customer_name=current_user.name,
            phone=telepon,
            guest_qty=int(jumlah_tamu),
            duration=int(durasi),
            notes=notes,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            status='pending'
        )
        db.session.add(new_reservation)
        db.session.flush() # Ambil ID reservasi yang baru dibuat tanpa commit dulu

        # 2. Simpan relasi banyak meja ke tabel 'reservation_tables'
        for m_id in meja_ids:
            target_table = Table.query.get(int(m_id))
            if target_table:
                new_res_table = ReservationTable(
                    reservation_id=new_reservation.id,
                    table_id=target_table.id,
                    table_number_snapshot=target_table.table_number
                )
                db.session.add(new_res_table)
        
        # Commit seluruh rangkaian transaksi database
        db.session.commit()

        flash('Reservasi Anda berhasil diajukan!', 'success')
        return jsonify({"success": True, "message": "Reservasi sukses dibuat."})

    except Exception as e:
        db.session.rollback()
        print(f"Error Database Reservasi: {str(e)}")
        return jsonify({"success": False, "message": f"Terjadi kesalahan internal: {str(e)}"}), 500
    
# Halaman Detail Reservasi Spesifik
@customer_bp.route('/reservasi/<int:reservation_id>')
@login_required
def reservasi_detail(reservation_id):
    reservation = Reservation.query.options(
        joinedload(Reservation.reserved_tables).joinedload(ReservationTable.table_ref)
    ).get_or_404(reservation_id)
    
    if reservation.user_id != current_user.id:
        flash('Anda tidak memiliki akses ke halaman ini!', 'danger')
        return redirect(url_for('customer.buat_reservasi'))

    # TAMBAHAN: Mengimpor dan mengonversi waktu created_at ke format lokal WIB
    from utils import format_tanggal_lokal, format_waktu_lokal
    if reservation.created_at:
        tanggal = format_tanggal_lokal(reservation.created_at)
        waktu = format_waktu_lokal(reservation.created_at)
        setattr(reservation, 'dibuat_pada_lokal', f"{tanggal}, {waktu}")
    else:
        setattr(reservation, 'dibuat_pada_lokal', '-')

    return render_template('customer/reservasi_detail.html', 
                           segment='buat_reservasi', 
                           role='customer', 
                           reservation=reservation)

# API Endpoint POST: Membatalkan Reservasi (dengan alasan) dari Alpine.js
@customer_bp.route('/reservasi/<int:reservation_id>/cancel', methods=['POST'])
@login_required
@role_required('customer')
def cancel_reservation(reservation_id):
    # Ambil data reservasi
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Keamanan: Pastikan hanya pemilik reservasi yang bisa membatalkan
    if reservation.user_id != current_user.id:
        return jsonify({"success": False, "message": "Anda tidak memiliki akses untuk tindakan ini!"}), 403
        
    # Pastikan reservasi masih dalam status yang bisa dibatalkan (pending / confirmed)
    if reservation.status not in ['pending', 'confirmed']:
        return jsonify({"success": False, "message": "Reservasi sudah selesai atau telah dibatalkan sebelumnya."}), 400
        
    # Ambil JSON payload alasan pembatalan dari Alpine.js fetch
    data = request.json
    reason = data.get('reason', '').strip() if data else ''
    
    if not reason:
        return jsonify({"success": False, "message": "Alasan pembatalan wajib diisi!"}), 400
        
    try:
        # Ubah status dan simpan alasannya ke database
        reservation.status = 'cancelled'
        reservation.cancellation_reason = reason
        
        db.session.commit()
        return jsonify({"success": True, "message": "Reservasi berhasil dibatalkan."})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Gagal memperbarui database: {str(e)}"}), 500

# Halaman Riwayat Reservasi
@customer_bp.route('/reservasi/history')
@login_required
@role_required('customer')
def reservasi_history():
    history_reservations = Reservation.query.options(
        joinedload(Reservation.reserved_tables).joinedload(ReservationTable.table_ref)
    ).filter(
        Reservation.user_id == current_user.id,
        Reservation.status.in_(['completed', 'cancelled'])
    ).order_by(Reservation.reservation_date.desc(), Reservation.reservation_time.desc()).all()
    
    return render_template('customer/reservasi_history.html', 
                           segment='buat_reservasi', 
                           role='customer', 
                           history_reservations=history_reservations)

# =========================
# MANAJEMEN PESANAN & CHECKOUT
# =========================

# API Endpoint POST: Menambahkan Item ke Keranjang (dari Alpine.js)
@customer_bp.route('/api/cart/add', methods=['POST'])
@login_required
@role_required('customer')
def add_to_cart():
    data = request.get_json()
    menu_id = data.get('menu_id')
    qty = int(data.get('qty', 1))
    menu = Menu.query.get_or_404(menu_id)

    # Cari cart aktif
    order = get_active_cart(current_user.id)

    # Jika belum ada cart
    if not order:
        order = Order(
            order_number=generate_order_number(),
            user_id=current_user.id,
            order_type='dine_in',
            payment_status='unpaid',
            order_status='pending',
            total_amount=0
        )

        db.session.add(order)
        db.session.flush()

    # Cek item sudah ada atau belum
    existing_item = OrderItem.query.filter_by(
        order_id=order.id,
        menu_id=menu.id
    ).first()

    if existing_item:
        existing_item.qty += qty

    else:
        new_item = OrderItem(
            order_id=order.id,
            menu_id=menu.id,
            qty=qty,
            price_at_order=menu.price
        )

        db.session.add(new_item)

    db.session.flush()

    # Update total
    total = sum(
        item.qty * item.price_at_order
        for item in order.items
    )

    order.total_amount = total
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Item berhasil ditambahkan'
    })

# API Endpoint GET: Mengambil Data Keranjang Aktif beserta item-itemnya (untuk Alpine.js)
@customer_bp.route('/api/cart')
@login_required
@role_required('customer')
def get_cart():
    order = get_active_cart(current_user.id, load_relations=True)

    if not order:
        return jsonify({
            'items': [],
            'subtotal': 0,
            'total': 0
        })

    items = []

    for item in order.items:
        items.append({
            'id': item.id,
            'menu_id': item.menu_id,
            'nama': item.menu.name,
            'harga': item.price_at_order,
            'qty': item.qty,
            'img': item.menu.image_url,
            'subtotal': item.qty * item.price_at_order,
            'note': item.notes if item.notes else ''
        })

    return jsonify({
        'order_id': order.id,
        'items': items,
        'subtotal': order.total_amount,
        'total': order.total_amount
    })

# API Endpoint POST: Update Quantity Item di Keranjang (dari Alpine.js)
@customer_bp.route('/api/cart/update', methods=['POST'])
@login_required
@role_required('customer')
def update_cart():
    data = request.get_json()
    item_id = data.get('item_id')
    qty = int(data.get('qty'))
    item = OrderItem.query.get_or_404(item_id)

    # Pastikan item milik user
    if item.order.user_id != current_user.id:
        return jsonify({
            'success': False
        }), 403
    
    order = item.order

    if qty <= 0:
        db.session.delete(item)
    else:
        item.qty = qty

    db.session.flush()
    total = recalculate_total(order)
    db.session.commit()

    return jsonify({
        'success': True,
        'total': total
    })

# API Endpoint DELETE: Menghapus Item dari Keranjang (dari Alpine.js)
@customer_bp.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
@login_required
@role_required('customer')
def remove_cart_item(item_id):

    item = OrderItem.query.get_or_404(item_id)

    if item.order.user_id != current_user.id:
        return jsonify({
            'success': False
        }), 403

    order = item.order
    db.session.delete(item)
    db.session.flush()

    order.total_amount = sum(
        i.qty * i.price_at_order
        for i in order.items
    )

    db.session.commit()

    return jsonify({
        'success': True
    })

# Halaman Daftar Pesanan Aktif & Riwayat Pesanan
@customer_bp.route('/pesanan-saya')
@login_required
@role_required('customer')
def pesanan_saya():
    # Mengambil semua pesanan milik user beserta relasi items dan review
    user_orders = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.review)
    ).filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    active_orders = []
    history_orders = []
    
    for o in user_orders:
        setattr(o, 'tanggal_lokal', format_tanggal_lokal(o.created_at))
        setattr(o, 'waktu_lokal', format_waktu_lokal(o.created_at))

        if o.payment_method is None:
            continue
            
        if o.payment_status == 'cancelled':
            history_orders.append(o)
            continue
            
        # Memeriksa apakah sudah ada ulasan pada salah satu item di pesanan ini
        has_review = any(item.review is not None for item in o.items)
        
        # Logika pemisahan status pesanan
        if o.order_status in ['pending', 'preparing', 'ready']:
            active_orders.append(o)
        elif o.order_status == 'served':
            if has_review:
                history_orders.append(o)
            else:
                # Jika sudah disajikan tetapi belum diulas, tetap masukkan ke Pesanan Aktif
                active_orders.append(o)
                
    return render_template('customer/pesanan_saya.html', 
                            segment='pesanan_saya', 
                            role='customer', 
                            active_orders=active_orders, 
                            history_orders=history_orders)

# Halaman Detail Pesanan Aktif & Riwayat Pesanan
@customer_bp.route('/pesanan-saya/history')
@login_required
@role_required('customer')
def pesanan_history():
    # Mengambil semua pesanan beserta relasi menu dan ulasan
    user_orders = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.menu),
        joinedload(Order.items).joinedload(OrderItem.review)
    ).filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()

    history_orders = []
    for o in user_orders:
        has_review = any(item.review is not None for item in o.items)
        
        # Riwayat hanya memuat pesanan yang dibatalkan ATAU pesanan disajikan yang TELAH diulas
        if o.payment_status == 'cancelled' or (o.order_status == 'served' and has_review):
            history_orders.append(o)

    return render_template(
        'customer/pesanan_history.html', 
        history_orders=history_orders, 
        segment='pesanan_saya', 
        role='customer'
    )

# Halaman Checkout: Menampilkan detail keranjang beserta opsi checkout
@customer_bp.route('/checkout')
@login_required
@role_required('customer')
def checkout():
    order = get_active_cart(current_user.id, load_relations=True)

    if not order:
        flash('Keranjang masih kosong', 'warning')
        return redirect(url_for('customer.daftar_menu'))

    tables = Table.query.filter_by(
        is_available=True
    ).all()

    return render_template(
        'customer/checkout.html',
        segment='daftar_menu',
        role='customer',
        order=order,
        tables=tables
    )

# Fitur "Pesan Lagi": Menyalin item dari pesanan lama ke keranjang aktif
@customer_bp.route('/pesan-lagi/<int:order_id>')
@login_required
@role_required('customer')
def pesan_lagi(order_id):
    old_order = Order.query.options(
        joinedload(Order.items)
    ).filter_by(id=order_id).first_or_404()

    # Perlindungan IDOR
    if old_order.user_id != current_user.id:
        abort(404)

    # Cari cart aktif
    active_order = get_active_cart(current_user.id)

    # Kalau belum ada cart
    if not active_order:
        active_order = Order(
            order_number=generate_order_number(),
            user_id=current_user.id,
            order_type='dine_in',
            payment_status='unpaid',
            order_status='pending',
            total_amount=0
        )

        db.session.add(active_order)
        db.session.flush()

    # Copy item
    for item in old_order.items:
        existing_item = OrderItem.query.filter_by(
            order_id=active_order.id,
            menu_id=item.menu_id
        ).first()

        if existing_item:
            existing_item.qty += item.qty

        else:
            new_item = OrderItem(
                order_id=active_order.id,
                menu_id=item.menu_id,
                qty=item.qty,
                price_at_order=item.price_at_order
            )
            db.session.add(new_item)

    db.session.flush()
    recalculate_total(active_order)
    db.session.commit()

    flash('Pesanan berhasil dimasukkan ke cart', 'success')
    return redirect(url_for('customer.checkout'))

# API Endpoint POST: Submit Pesanan dari Checkout (dari Alpine.js)
@customer_bp.route('/submit-order', methods=['POST'])
@login_required
@role_required('customer')
def submit_order():
    data = request.get_json()
    order = get_active_cart(current_user.id)

    if not order:
        return jsonify({
            'success': False,
            'message': 'Cart kosong'
        })

    # Ambil tipe pesanan dari data (default: dine_in)
    order_type = data.get('order_type', 'dine_in')
    order.order_type = order_type

    # Logika pengisian meja berdasarkan tipe pesanan
    if order_type == 'dine_in':
        table_ids = data.get('table_ids', [])
        
        if table_ids:
            # Tetap simpan ID meja pertama ke kolom table_id sebagai backward-compatibility
            order.table_id = int(table_ids[0])
            
            # Merakit nama meja yang dipilih untuk snapshot
            selected_tables = Table.query.filter(Table.id.in_(table_ids)).all()
            table_names = [t.table_number for t in selected_tables]
            
            # Simpan seluruh nama meja (dipisah koma) ke kolom snapshot
            order.table_number_snapshot = ", ".join(table_names)
            
            # Ubah status ketersediaan meja menjadi tidak tersedia (Opsional tapi disarankan)
            for t in selected_tables:
                t.is_available = False
                
    else:
        # Jika take away, pastikan kolom meja dikosongkan
        order.table_id = None
        order.table_number_snapshot = None

    order.payment_method = data.get('payment_method')
    order.order_status = 'pending'

    db.session.commit()

    return jsonify({
        'success': True,
        'order_id': order.id
    })

# API Endpoint POST: Update Catatan untuk Item di Keranjang (dari Alpine.js)
@customer_bp.route('/api/cart/note', methods=['POST'])
@login_required
@role_required('customer')
def update_cart_note():
    data = request.get_json()
    item_id = data.get('item_id')
    note = data.get('note')
    item = OrderItem.query.get_or_404(item_id)

    if item.order.user_id != current_user.id:
        return jsonify({
            'success': False
        }), 403

    item.notes = note
    db.session.commit()

    return jsonify({
        'success': True
    })

# Halaman Detail Pesanan: Menampilkan detail pesanan beserta item, status, dan ulasan jika sudah disajikan
@customer_bp.route('/pesanan/<int:order_id>')
@login_required
@role_required('customer')
def pesanan_detail(order_id):
# Mengambil data order beserta relasi items, menu, dan review secara eksplisit
    order = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.menu),
        joinedload(Order.items).joinedload(OrderItem.review)
    ).filter_by(id=order_id).first_or_404()

    # Perlindungan IDOR
    if order.user_id != current_user.id:
        abort(404)

    # PERBAIKAN LOGIKA: Cek apakah pesanan sudah memiliki ulasan pada item-itemnya
    has_review = any(item.review is not None for item in order.items)

    # Pesanan masuk ke riwayat HANYA JIKA dibatalkan, ATAU (sudah served DAN sudah diulas)
    is_history = order.payment_status == 'cancelled' or (order.order_status == 'served' and has_review)

    order_dict = {
        'id': order.id,
        'order_number': order.order_number,
        'customer_name': order.customer_name or current_user.name,
        'payment_method': order.payment_method,
        'payment_status': order.payment_status,
        'order_status': order.order_status,
        'order_type': order.order_type,
        'no_meja': order.table_number_snapshot if order.table_number_snapshot else ('-' if order.order_type == 'take_away' else 'Meja tidak valid'),
        'total_amount': order.total_amount,
        'items': [{
            'id': item.id,
            'nama': item.menu.name,
            'harga': item.price_at_order,
            'qty': item.qty,
            'img': item.menu.image_url,
            'note': item.notes,
            'rating': item.review.rating if item.review else None, 
            'comment': item.review.comment if item.review else None 
        } for item in order.items]
    }

    # Jika pesanan sudah selesai/batal, arahkan ke halaman baru
    if is_history:
        return render_template(
            'customer/pesanan_riwayat_detail.html',
            segment='pesanan_saya',
            role='customer',
            order=order,
            order_json=order_dict
        )

    return render_template(
        'customer/pesanan_aktif_detail.html',
        segment='pesanan_saya',
        role='customer',
        order=order,
        order_json=order_dict
    )

# Halaman Pembayaran Non-Tunai: Menampilkan detail pesanan dan instruksi pembayaran untuk metode non-tunai
@customer_bp.route('/pembayaran-nontunai/<int:order_id>')
@login_required
@role_required('customer')
def pembayaran_nontunai(order_id):
    # Ambil data order
    order = Order.query.filter_by(id=order_id).first_or_404()
    
    # Perlindungan IDOR
    if order.user_id != current_user.id:
        abort(404)
    
    # Ambil data penting untuk dikirim ke Alpine.js secara aman
    order_data = {
        'order_id': order.id,
        'customer_name': order.customer_name or current_user.name,
        'total_amount': order.total_amount
    }
    
    return render_template(
        'customer/pembayaran_nontunai.html',
        role='customer',
        order_id=order_id,
        order_json=order_data
    )

# API Endpoint POST: Submit Ulasan untuk Pesanan yang Sudah Disajikan (dari Alpine.js)
@customer_bp.route('/api/submit-reviews', methods=['POST'])
@login_required
@role_required('customer')
def submit_reviews():
    data = request.get_json()
    order_id = data.get('order_id')
    reviews_data = data.get('reviews', [])

    # Validasi kepemilikan pesanan
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        return jsonify({"success": False, "message": "Pesanan tidak ditemukan!"}), 404

    try:
        for rev in reviews_data:
            item_id = rev.get('item_id')
            rating = rev.get('rating')
            comment = rev.get('comment')

            # Lewati jika rating atau komentar kosong
            if not rating or not comment.strip():
                continue

            # Validasi bahwa item tersebut benar milik pesanan ini
            item = OrderItem.query.filter_by(id=item_id, order_id=order.id).first()
            if item:
                # Cek apakah sudah pernah diulas sebelumnya
                if not item.review:
                    new_review = Review(
                        order_item_id=item.id,
                        rating=int(rating),
                        comment=comment.strip()
                    )
                    db.session.add(new_review)
        
        db.session.commit()
        return jsonify({"success": True, "message": "Ulasan berhasil disimpan"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Terjadi kesalahan: {str(e)}"}), 500

# API Endpoint DELETE: Menghapus Semua Item dari Keranjang (dari Alpine.js)
@customer_bp.route('/api/cart/clear', methods=['DELETE'])
@login_required
@role_required('customer')
def clear_cart():
    order = get_active_cart(current_user.id)

    if not order:
        return jsonify({
            'success': False,
            'message': 'Keranjang sudah kosong'
        }), 400

    # Menghapus seluruh item yang terhubung dengan pesanan aktif ini
    for item in order.items:
        db.session.delete(item)
    
    order.total_amount = 0
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Semua item berhasil dihapus'
    })

# =========================
# PENGATURAN PROFIL
# =========================

# Halaman Pengaturan Profil: Menampilkan form untuk mengubah data profil dan foto pengguna
@customer_bp.route('/pengaturan', methods=['GET', 'POST'])
@login_required
@role_required('customer')
def pengaturan():
    if request.method == 'POST':
        phone_input = request.form.get('phone')

        # Validasi Nomor Telepon (Harus berupa angka saja jika diisi)
        if phone_input and not phone_input.isdigit():
            return jsonify({"success": False, "message": "Nomor telepon hanya boleh berisi angka!"})
        
        current_user.name = request.form.get('name')
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.phone = phone_input

        # Konsisten menggunakan 'photo'
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                upload_path = os.path.join(current_app.root_path, 'static/uploads/profile')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

                # Logika aman penghapusan foto lama (cek folder images maupun uploads)
                if current_user.photo:
                    old_path = os.path.join(current_app.root_path, 'static', current_user.photo)
                    if not os.path.exists(old_path) and not current_user.photo.startswith('uploads/'):
                        old_path = os.path.join(current_app.root_path, 'static/images', current_user.photo)
                        
                    if os.path.exists(old_path) and os.path.isfile(old_path):
                        try: os.remove(old_path)
                        except: pass
                
                filename = secure_filename(file.filename)
                unique_filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                
                # Simpan fisik
                file.save(os.path.join(upload_path, unique_filename))
                
                # Simpan beserta alamat path relatifnya ke database
                current_user.photo = f"uploads/profile/{unique_filename}"

        try:
            db.session.commit()
            # PERUBAHAN: Mengembalikan JSON sukses (bukan flash & redirect)
            return jsonify({"success": True, "message": "Profil berhasil diperbarui!"})
        except Exception:
            db.session.rollback()
            # PERUBAHAN: Mengembalikan JSON gagal
            return jsonify({"success": False, "message": "Gagal memperbarui profil. Username/Email mungkin sudah digunakan."})

    return render_template('customer/pengaturan.html', segment='pengaturan', role='customer', user=current_user)

# API Endpoint POST: Update Kata Sandi Pengguna (dari Alpine.js)
@customer_bp.route('/api/update-password', methods=['POST'])
@login_required
@role_required('customer')
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