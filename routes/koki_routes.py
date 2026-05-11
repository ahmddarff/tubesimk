from flask import Blueprint, render_template, request, jsonify

koki_bp = Blueprint('koki', __name__)

orders_data = [
    {
        "id": 1, "id_display": "ORD001",
        "waktu": "14:00", "meja": "Meja 3",
        "status": "pending",
        "items": [
            {"nama": "Ayam Geprek",  "qty": 2, "catatan": "Pedas level 3"},
            {"nama": "Americano",    "qty": 1, "catatan": ""},
            {"nama": "Indomie Kuah", "qty": 1, "catatan": "Tambah telur"},
        ]
    },
    {
        "id": 2, "id_display": "ORD002",
        "waktu": "14:05", "meja": "Meja 1",
        "status": "pending",
        "items": [
            {"nama": "Nasi Goreng",  "qty": 1, "catatan": "Tidak pedas"},
            {"nama": "Matcha",       "qty": 2, "catatan": ""},
        ]
    },
    {
        "id": 3, "id_display": "ORD003",
        "waktu": "13:45", "meja": "Meja 5",
        "status": "preparing",
        "items": [
            {"nama": "Beef Teriyaki",  "qty": 1, "catatan": ""},
            {"nama": "Vanilla Latte",  "qty": 1, "catatan": "Less sugar"},
            {"nama": "Kentang Goreng", "qty": 2, "catatan": "Extra saus"},
        ]
    },
    {
        "id": 4, "id_display": "ORD004",
        "waktu": "13:30", "meja": "Meja 2",
        "status": "preparing",
        "items": [
            {"nama": "Dimsum",      "qty": 3, "catatan": ""},
            {"nama": "Americano",   "qty": 2, "catatan": "Hot"},
        ]
    },
    {
        "id": 5, "id_display": "ORD005",
        "waktu": "13:15", "meja": "Meja 7",
        "status": "ready",
        "items": [
            {"nama": "Indomie Goreng", "qty": 2, "catatan": ""},
            {"nama": "Matcha",         "qty": 1, "catatan": ""},
        ]
    },
    {
        "id": 6, "id_display": "ORD006",
        "waktu": "13:00", "meja": "Meja 4",
        "status": "ready",
        "items": [
            {"nama": "Nasi Goreng", "qty": 1, "catatan": "Extra nasi"},
            {"nama": "Americano",   "qty": 1, "catatan": ""},
        ]
    },
]

# (data lainnya seperti sebelumnya — menu_data, kasir_data, dll.)

# ── Koki Routes ───────────────────────────────────────
@koki_bp.route('/dashboard')
def koki_dashboard():
    return render_template('koki/koki_dashboard.html',
        username="Budi",
        orders=[],
        menu_list=[]
    )

@koki_bp.route('/api/koki/update-order-status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    data = request.json
    for o in orders_data:
        if o['id'] == order_id:
            o['status'] = data.get('status', o['status'])
            break
    return jsonify({"success": True, "message": "Status order diperbarui!"})

@koki_bp.route('/api/koki/update-stok/<int:menu_id>', methods=['POST'])
def koki_update_stok(menu_id):
    data = request.json
    for m in menu_data:
        if m['id'] == menu_id:
            m['stok'] = int(data.get('stok', m['stok']))
            # Auto set status False jika stok 0
            if m['stok'] == 0:
                m['status'] = False
            break
    return jsonify({"success": True, "message": "Stok berhasil diperbarui!"})