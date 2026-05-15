import os, random, string
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from models import User, Menu, Category, Order, OrderItem, Table, Reservation
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

@customer_bp.route('/menu/<int:menu_id>/ulasan')
def menu_reviews(menu_id):
    # Mengambil data menu dari basis data berdasarkan ID
    menu = Menu.query.get_or_404(menu_id)
    
    return render_template('customer/menu_reviews.html', 
                           menu=menu, 
                           segment='daftar_menu', 
                           role='customer')

@customer_bp.route('/buat-reservasi')
@login_required
def buat_reservasi():
    # Mengambil semua reservasi milik pengguna yang sedang masuk (login)
    user_reservations = Reservation.query.filter_by(user_id=current_user.id)\
        .order_by(Reservation.reservation_date.desc(), Reservation.reservation_time.desc()).all()
    
    # Memisahkan reservasi aktif (pending, confirmed)
    active_reservations = [r for r in user_reservations if r.status in ['pending', 'confirmed']]
    
    # Memisahkan riwayat reservasi (completed, cancelled)
    history_reservations = [r for r in user_reservations if r.status in ['completed', 'cancelled']]
    
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