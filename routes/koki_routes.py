import os
from utils import *
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import Order, OrderItem, Menu
from extensions import db

koki_bp = Blueprint('koki', __name__)

# =========================
# ANTREAN ORDER KOKI
# =========================
@koki_bp.route('/antrean-order')
@login_required
@role_required('koki')
def antrian():
    # PROTEKSI ANTI-FIKTIF: Kasir boleh unpaid, Pesanan Mandiri aplikasi wajib PAID!
    orders_db = Order.query.filter(
        Order.order_status.in_(['pending', 'preparing', 'ready']),
        Order.payment_status != 'cancelled',
        db.or_(
            Order.user_id.is_(None), 
            db.and_(Order.user_id.isnot(None), Order.payment_status == 'paid')
        )
    ).order_by(Order.created_at.asc()).all()
    
    pending_count = sum(1 for o in orders_db if o.order_status == 'pending')
    
    formatted_orders = []
    for o in orders_db:
        items_list = []
        for item in o.items:
            items_list.append({
                "id": item.id,
                "nama": item.menu.name if item.menu else "Menu Terhapus",
                "tipe_kategori": item.menu.category.type if item.menu and item.menu.category else "food",
                "qty": item.qty,
                "catatan": item.notes or "",
                "status": item.item_status
            })
            
        info_meja = o.table_number_snapshot if o.table_number_snapshot else "Take Away"
        if o.order_type == 'dine_in' and o.table_number_snapshot:
            info_meja = f"Meja {o.table_number_snapshot}"

        formatted_orders.append({
            "id": o.id,
            "id_display": o.order_number,
            "waktu_iso": o.created_at.isoformat() + 'Z',
            "meja": info_meja,
            "sumber": "Aplikasi" if o.user_id else "Kasir",
            "status": o.order_status,
            "items": items_list
        })

    return render_template('koki/antrean_order.html',
        username=current_user.name,
        orders=formatted_orders,
        pending_count=pending_count
    )

# =========================
# STOK MENU KOKI
# =========================
@koki_bp.route('/stok-menu')
@login_required
@role_required('koki')
def stok():
    pending_count = Order.query.filter_by(order_status='pending').count()
    menus_db = Menu.query.all()
    
    formatted_menus = []
    for m in menus_db:
        formatted_menus.append({
            "id": m.id,
            "nama": m.name,
            "kategori": m.category.name if m.category else "-",
            "stok": m.stock,
            "status": m.is_available,
            "img": m.image_url or "" # ✅ BARU: Sekarang data foto dikirim ke frontend koki
        })

    return render_template('koki/stok_menu.html',
        username=current_user.name,
        menu_list=formatted_menus,
        pending_count=pending_count
    )

# =========================
# PENGATURAN PROFIL KOKI
# =========================
@koki_bp.route('/pengaturan', methods=['GET', 'POST'])
@login_required
@role_required('koki')
def pengaturan():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')

        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                upload_path = os.path.join(current_app.root_path, 'static/uploads/profile')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

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
                current_user.photo = f"uploads/profile/{unique_filename}"

        try:
            db.session.commit()
            return jsonify({"success": True, "message": "Profil berhasil diperbarui!"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": "Gagal memperbarui profil. Username atau email mungkin sudah digunakan."})

    pending_count = Order.query.filter_by(order_status='pending').count()
    return render_template('koki/pengaturan.html',
        username=current_user.name,
        pending_count=pending_count
    )

@koki_bp.route('/api/update-password', methods=['POST'])
@login_required
@role_required('koki')
def update_password():
    data = request.json
    password_lama = data.get("password_lama")
    password_baru = data.get("password_baru")
    
    if not check_password_hash(current_user.password, password_lama):
        return jsonify({"success": False, "message": "Kata sandi saat ini salah!"})
    
    current_user.password = generate_password_hash(password_baru)
    
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Kata sandi berhasil diperbarui!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Gagal menyimpan kata sandi baru."})
    
# ── ANTREAN ORDER APIS ──────────────────────────────────────────────
@koki_bp.route('/api/koki/update-item-status', methods=['POST'])
@login_required
@role_required('koki')
def update_item_status():
    data = request.json
    item_id = data.get('item_id')
    new_status = data.get('status')
    
    if not item_id:
        return jsonify({"success": False, "message": "ID Item wajib disertakan."}), 400
    
    try:
        item = db.session.get(OrderItem, int(item_id))
        if not item:
            return jsonify({"success": False, "message": "Item menu tidak ditemukan."}), 404
        
        item.item_status = new_status
        
        auto_sync_order_status(item.order)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Status {item.menu.name if item.menu else 'item'} berhasil diperbarui!",
            "new_order_status": item.order.order_status
        })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    
@koki_bp.route('/api/koki/update-kitchen-status-bulk', methods=['POST'])
@login_required
@role_required('koki')
def update_kitchen_status_bulk():
    data = request.json
    item_ids = data.get('item_ids', [])
    new_status = data.get('status')
    
    if not item_ids:
        return jsonify({"success": False, "message": "Tidak ada item untuk diproses."})
        
    # Tarik semua item yang id-nya ada di dalam daftar item_ids
    items = OrderItem.query.filter(OrderItem.id.in_(item_ids)).all()
    if not items:
        return jsonify({"success": False, "message": "Item tidak ditemukan."})
        
    # Ambil data induk order dari item pertama
    order = items[0].order
    
    # Update semua item yang terpilih
    for item in items:
        item.item_status = new_status
        
    # Panggil fungsi pintar buatanmu untuk sinkronisasi induknya (cukup 1x jalan!)
    auto_sync_order_status(order)
    
    try:
        db.session.commit()
        # Kembalikan status induk terbaru ke frontend
        return jsonify({"success": True, "new_order_status": order.order_status})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

# ── STOCK MENU APIS ──────────────────────────────────────────────
@koki_bp.route('/api/koki/update-order-status/<int:order_id>', methods=['POST'])
@login_required
@role_required('koki')
def update_order_status(order_id):
    data = request.json
    status_baru = data.get('status')
    
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"success": False, "message": "Pesanan tidak ditemukan."}), 404
        
    try:
        order.order_status = status_baru
        db.session.commit()
        return jsonify({"success": True, "message": f"Status pesanan {order.order_number} diperbarui!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    
@koki_bp.route('/api/koki/update-stok/<int:menu_id>', methods=['POST'])
@login_required
@role_required('koki')
def update_stok(menu_id):
    data = request.json
    stok_baru = data.get('stok')
    
    menu = db.session.get(Menu, menu_id)
    if not menu:
        return jsonify({"success": False, "message": "Menu tidak ditemukan."}), 404
        
    try:
        if stok_baru is not None and str(stok_baru).strip() != "":
            menu.stock = int(stok_baru)
            if menu.stock == 0:
                menu.is_available = False
            elif menu.stock > 0:
                menu.is_available = True
                
        db.session.commit()
        return jsonify({"success": True, "message": f"Stok {menu.name} diperbarui!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    
@koki_bp.route('/api/koki/toggle-menu-status/<int:menu_id>', methods=['POST'])
@login_required
@role_required('koki')
def toggle_menu_status(menu_id):
    data = request.json
    menu = db.session.get(Menu, menu_id)
    if menu:
        menu.is_available = data.get("status")
        try:
            db.session.commit()
            return jsonify({"success": True, "message": f"Status menu {menu.name} berhasil diperbarui!"})
        except:
            db.session.rollback()
            return jsonify({"success": False, "message": "Gagal memperbarui status menu."})
    return jsonify({"success": False, "message": "Menu tidak ditemukan."}), 404