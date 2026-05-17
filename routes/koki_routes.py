from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import Order, OrderItem, Menu
from extensions import db

koki_bp = Blueprint('koki', __name__)

# ── 1. ROUTE ANTREAN ORDER (DINAMIS DATABASE) ─────────────────────────────────
@koki_bp.route('/antrean-order')
@login_required
def koki_antrian():
    # Ambil order yang statusnya pending, preparing, atau ready (belum served/selesai)
    orders_db = Order.query.filter(Order.order_status.in_(['pending', 'preparing', 'ready']))\
                           .order_by(Order.created_at.asc()).all()
    
    # Hitung jumlah antrean baru (pending) untuk indikator badge navbar koki
    pending_count = Order.query.filter_by(order_status='pending').count()
    
    # Mapping data DB ke struktur JSON/Dictionary agar template HTML Koki tidak pecah
    formatted_orders = []
    for o in orders_db:
        items_list = []
        for item in o.items:
            items_list.append({
                "nama": item.menu.name,
                "qty": item.qty,
                "catatan": item.notes or ""
            })
            
        formatted_orders.append({
            "id": o.id,
            "id_display": o.order_number,
            "waktu": o.created_at.strftime("%H:%M"),
            "meja": f"Meja {o.table.table_number}" if o.table_id else "Take Away",
            "status": o.order_status,
            "items": items_list
        })

    return render_template('koki/antrean-order.html',
        username=current_user.name,
        orders=formatted_orders,
        pending_count=pending_count
    )

# ── 2. ROUTE MANAJEMEN STOK KOKI (DINAMIS DATABASE) ───────────────────────────
@koki_bp.route('/stok-menu')
@login_required
def koki_stok():
    pending_count = Order.query.filter_by(order_status='pending').count()
    
    # Ambil semua data menu dari database
    menus_db = Menu.query.all()
    
    # Mapping agar sesuai dengan kebutuhan loop template stok koki
    formatted_menus = []
    for m in menus_db:
        formatted_menus.append({
            "id": m.id,
            "nama": m.name,
            "kategori": m.category.name if m.category else "-",
            "stok": m.stock, # Bisa bernilai None (unlimited) atau Integer
            "status": m.is_available
        })

    return render_template('koki/stok-menu.html',
        username=current_user.name,
        menu_list=formatted_menus,
        pending_count=pending_count
    )

# ── 3. ROUTE PENGATURAN KOKI ──────────────────────────────────────────────────
@koki_bp.route('/pengaturan')
@login_required
def koki_pengaturan():
    pending_count = Order.query.filter_by(order_status='pending').count()
    return render_template('koki/pengaturan.html',
        username=current_user.name,
        pending_count=pending_count
    )

# ── 4. API UPDATE STATUS PESANAN (LIVE UPDATE TO DATABASE) ────────────────────
@koki_bp.route('/api/koki/update-order-status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    data = request.json
    status_baru = data.get('status')
    
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"success": False, "message": "Pesanan tidak ditemukan."}), 404
        
    try:
        order.order_status = status_baru
        db.session.commit()
        return jsonify({"success": True, "message": f"Status pesanan {order.order_number} diperbarui menjadi {status_baru}!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# ── 5. API UPDATE STOK CEPAT DARI KOKI (LIVE UPDATE TO DATABASE) ──────────────
@koki_bp.route('/api/koki/update-stok/<int:menu_id>', methods=['POST'])
@login_required
def koki_update_stok(menu_id):
    data = request.json
    stok_baru = data.get('stok')
    
    menu = db.session.get(Menu, menu_id)
    if not menu:
        return jsonify({"success": False, "message": "Menu tidak ditemukan."}), 404
        
    try:
        # ✅ REVISI: Bersihkan baris stok_arrows dan beri validasi null-safe
        if stok_baru is not None and str(stok_baru).strip() != "":
            menu.stock = int(stok_baru)
            
            # Auto set status ketersediaan menjadi False (habis) jika stok diatur ke angka 0
            if menu.stock == 0:
                menu.is_available = False
            elif menu.stock > 0:
                menu.is_available = True
                
        db.session.commit()
        return jsonify({"success": True, "message": f"Stok {menu.name} berhasil diperbarui!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500