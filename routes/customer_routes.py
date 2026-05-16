import os, random, string
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from models import User, Menu, Category, Order, OrderItem, Table, Reservation, ReservationTable
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
    
    # Menyaring semua item pesanan dari menu ini
    order_items = OrderItem.query.filter_by(menu_id=menu.id).all()
    
    reviews = []
    total_rating = 0
    
    for item in order_items:
        # Jika item pesanan ini memiliki ulasan
        if item.review:
            # Menentukan nama pelanggan
            nama_pelanggan = "Pelanggan Anonim"
            if item.order.user:
                nama_pelanggan = item.order.user.name
            elif item.order.customer_name:
                nama_pelanggan = item.order.customer_name
                
            reviews.append({
                'nama': nama_pelanggan,
                'date': item.review.created_at.strftime('%d %b %Y'),
                'rating': item.review.rating,
                'text': item.review.comment
            })
            total_rating += item.review.rating
            
    # Kalkulasi statistik ulasan
    review_count = len(reviews)
    avg_rating = round(total_rating / review_count, 1) if review_count > 0 else 0
    
    return render_template('customer/menu_detail.html', 
            menu=menu,
            reviews=reviews,          # Kirim data array ulasan
            avg_rating=avg_rating,    # Kirim nilai rata-rata rating
            review_count=review_count,# Kirim total jumlah ulasan
            segment='daftar_menu', 
            role='customer')

@customer_bp.route('/menu/<int:menu_id>/ulasan')
def menu_reviews(menu_id):
    # Mengambil data menu dari basis data
    menu = Menu.query.get_or_404(menu_id)
    
    # Menyaring semua item pesanan dari menu ini
    order_items = OrderItem.query.filter_by(menu_id=menu.id).all()
    
    reviews = []
    total_rating = 0
    
    for item in order_items:
        # Jika item pesanan ini memiliki ulasan
        if item.review:
            # Menentukan nama pelanggan
            nama_pelanggan = "Pelanggan Anonim"
            if item.order.user:
                nama_pelanggan = item.order.user.name
            elif item.order.customer_name:
                nama_pelanggan = item.order.customer_name
                
            reviews.append({
                'nama': nama_pelanggan,
                'date': item.review.created_at.strftime('%d %b %Y'),
                'rating': item.review.rating,
                'text': item.review.comment
            })
            total_rating += item.review.rating
            
    # Kalkulasi statistik ulasan
    review_count = len(reviews)
    avg_rating = round(total_rating / review_count, 1) if review_count > 0 else 0
    
    return render_template('customer/menu_reviews.html', 
            menu=menu,
            reviews=reviews,          # Kirim data array ulasan
            avg_rating=avg_rating,    # Kirim nilai rata-rata rating
            review_count=review_count,# Kirim total jumlah ulasan
            segment='daftar_menu', 
            role='customer')


# =========================
# RESERVASI
# =========================

# Halaman List Reservasi Aktif & Riwayat
@customer_bp.route('/buat-reservasi')
@login_required
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
def reservasi_new():
    # Mengambil semua data meja yang berstatus tersedia
    tables = Table.query.filter_by(is_available=True).all()
    return render_template('customer/buat_reservasi_new.html', 
                           segment='buat_reservasi', 
                           role='customer',
                           tables=tables)

# API Endpoint POST: Menerima data JSON dari Submit Alpine.js
@customer_bp.route('/buat-reservasi/submit', methods=['POST'])
@login_required
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

        # Buat kode reservation_number dengan format RSV-YYYYMMDD-XXX
        today_str = datetime.today().strftime('%Y%m%d')
        prefix = f"RSV-{today_str}-"
        
        # Mencari reservasi terakhir yang dibuat pada hari ini
        last_reservation = Reservation.query.filter(
            Reservation.reservation_number.like(f"{prefix}%")
        ).order_by(Reservation.id.desc()).first()
        
        if last_reservation:
            # Mengambil 3 digit terakhir dan menambahkannya dengan 1
            last_seq = int(last_reservation.reservation_number.split('-')[-1])
            new_seq = last_seq + 1
        else:
            # Jika belum ada reservasi hari ini, mulai dari 1
            new_seq = 1
            
        # Memformat nomor urut agar selalu 3 digit (contoh: 001, 002)
        reservation_number = f"{prefix}{new_seq:03d}"

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

    return render_template('customer/reservasi_detail.html', 
                           segment='buat_reservasi', 
                           role='customer', 
                           reservation=reservation)

@customer_bp.route('/reservasi/<int:reservation_id>/cancel', methods=['POST'])
@login_required
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

@customer_bp.route('/reservasi/history')
@login_required
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

@customer_bp.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():

    data = request.get_json()

    menu_id = data.get('menu_id')
    qty = int(data.get('qty', 1))

    menu = Menu.query.get_or_404(menu_id)

    # Cari cart aktif
    order = Order.query.filter_by(
        user_id=current_user.id,
        order_status='pending',
        payment_status='unpaid'
    ).first()

    # Jika belum ada cart
    if not order:

        order_number = 'ORD-' + ''.join(
            random.choices(string.digits, k=6)
        )

        order = Order(
            order_number=order_number,
            user_id=current_user.id,
            customer_name=current_user.name,
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

@customer_bp.route('/api/cart')
@login_required
def get_cart():

    order = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.menu)
    ).filter_by(
        user_id=current_user.id,
        order_status='pending',
        payment_status='unpaid'
    ).first()

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
            'subtotal': item.qty * item.price_at_order
        })

    return jsonify({
        'order_id': order.id,
        'items': items,
        'subtotal': order.total_amount,
        'total': order.total_amount
    })

@customer_bp.route('/api/cart/update', methods=['POST'])
@login_required
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

    if qty <= 0:
        db.session.delete(item)

    else:
        item.qty = qty

    db.session.flush()

    order = item.order

    # Recalculate total
    total = sum(
        i.qty * i.price_at_order
        for i in order.items
    )

    order.total_amount = total

    db.session.commit()

    return jsonify({
        'success': True,
        'total': total
    })

@customer_bp.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
@login_required
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

@customer_bp.route('/pesanan-saya')
@login_required
def pesanan_saya():
    # Mengambil semua pesanan milik user yang sedang login
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    # Memisahkan pesanan Aktif dan Riwayat
    active_orders = [
        o for o in user_orders
        if o.order_status in ['pending', 'preparing', 'ready']
        and o.payment_status != 'cancelled'
    ]
    history_orders = [o for o in user_orders if (o.order_status == 'served' and o.payment_status == 'paid') or o.payment_status == 'cancelled']
    
    return render_template('customer/pesanan_saya.html', 
                            segment='pesanan_saya', 
                            role='customer', 
                            active_orders=active_orders, 
                            history_orders=history_orders)

@customer_bp.route('/pesanan-saya/history')
def pesanan_history():
# Ambil pesanan dari database murni yang statusnya sudah disajikan (served)
    history_orders = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.menu)
    ).filter(
        Order.user_id == current_user.id,
        Order.order_status == 'served'
    ).order_by(Order.created_at.desc()).all()

    return render_template(
        'customer/pesanan_history.html', 
        history_orders=history_orders, 
        segment='pesanan_saya', 
        role='customer'
    )

@customer_bp.route('/checkout')
@login_required
def checkout():

    order = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.menu)
    ).filter_by(
        user_id=current_user.id,
        order_status='pending',
        payment_status='unpaid'
    ).first()

    if not order:
        flash('Keranjang masih kosong', 'warning')
        return redirect(url_for('customer.daftar_menu'))

    tables = Table.query.filter_by(
        is_available=True
    ).all()

    return render_template(
        'customer/checkout.html',
        segment='checkout',
        role='customer',
        order=order,
        tables=tables
    )

@customer_bp.route('/pesan-lagi/<int:order_id>')
@login_required
def pesan_lagi(order_id):

    old_order = Order.query.options(
        joinedload(Order.items)
    ).filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    # Cari cart aktif
    active_order = Order.query.filter_by(
        user_id=current_user.id,
        order_status='pending',
        payment_status='unpaid'
    ).first()

    # Kalau belum ada cart
    if not active_order:

        active_order = Order(
            order_number='ORD-' + ''.join(random.choices(string.digits, k=6)),
            user_id=current_user.id,
            customer_name=current_user.name,
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

    active_order.total_amount = sum(
        i.qty * i.price_at_order
        for i in active_order.items
    )

    db.session.commit()

    flash('Pesanan berhasil dimasukkan ke cart', 'success')

    return redirect(url_for('customer.checkout'))

@customer_bp.route('/submit-order', methods=['POST'])
@login_required
def submit_order():
    data = request.get_json()

    order = Order.query.filter_by(
        user_id=current_user.id,
        order_status='pending',
        payment_status='unpaid'
    ).first()

    if not order:
        return jsonify({
            'success': False,
            'message': 'Cart kosong'
        })

    # Update nama pemesan terbaru dari input checkout
    nama_pemesan = data.get('nama')
    if nama_pemesan:
        order.customer_name = nama_pemesan

    # Ambil table jika dine in
    table_id = data.get('table_id')
    if table_id:
        table = Table.query.get(table_id)
        if table:
            order.table_id = table.id

    order.payment_method = data.get('payment_method')

    # Jika QRIS → langsung paid
    if order.payment_method == 'qris':
        order.payment_status = 'paid'

    order.order_status = 'preparing'

    db.session.commit()

    return jsonify({
        'success': True,
        'order_id': order.id
    })

@customer_bp.route('/api/cart/note', methods=['POST'])
@login_required
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

@customer_bp.route('/pesanan/<int:order_id>')
@login_required
def pesanan_detail(order_id):

    order = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.menu)
    ).filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    # Konversi objek SQLAlchemy menjadi dictionary murni agar aman di-serialize ke JSON
    order_dict = {
        'id': order.id,
        'order_number': order.order_number,
        'customer_name': order.customer_name,
        'payment_method': order.payment_method,
        'order_status': order.order_status,
        'total_amount': order.total_amount,
        'items': [{
            'nama': item.menu.name,
            'harga': item.price_at_order,
            'qty': item.qty,
            'note': item.notes
        } for item in order.items]
    }

    return render_template(
        'customer/pesanan_aktif_detail.html',
        segment='pesanan_saya',
        role='customer',
        order=order,
        order_json=order_dict
    )

@customer_bp.route('/pesanan/<order_id>/selesai')
def pesanan_selesai(order_id):
    if 'orders' in session and order_id in session['orders']:
        session['orders'][order_id]['status'] = 'Selesai'
        session.modified = True
    
    order = session.get('orders', {}).get(order_id)
    return render_template('customer/pesanan_selesai.html', segment='pesanan_saya', role='customer', order=order, order_id=order_id)

@customer_bp.route('/pembayaran-nontunai/<int:order_id>')
@login_required
def pembayaran_nontunai(order_id):
    # Ambil data order milik user yang sedang login
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    # Ambil data penting untuk dikirim ke Alpine.js secara aman
    order_data = {
        'order_id': order.id,
        'customer_name': order.customer_name,
        'total_amount': order.total_amount
    }
    
    return render_template(
        'customer/pembayaran_nontunai.html',
        role='customer',
        order_id=order_id,
        order_json=order_data
    )


# =========================
# PENGATURAN PROFIL
# =========================

@customer_bp.route('/pengaturan', methods=['GET', 'POST'])
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