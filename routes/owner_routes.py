from flask import Blueprint, render_template, request, jsonify

owner_bp = Blueprint('owner', __name__)

@owner_bp.route('/dashboard')
def dashboard():
    return render_template('owner/dashboard.html')

# Mock Data Owner
profil_cafe = {
    "nama":   "Terralog Coffee & Eatery",
    "telp":   "+62 812-XXXX-XXXX",
    "alamat": "Jl. Aman I No.2, Teladan Bar., Kec. Medan Kota, Kota Medan, Sumatera Utara 20216",
    "email":  "hello@terralog.com",
}

akun_owner = {
    "nama":      "Oscar Piastri",
    "panggilan": "Oscar",
    "email":     "oscar.owner@gmail.com",
    "no_hp":     "0812-xxxx-xxxx",
    "jabatan":   "Owner/Pemilik",
}

jam_operasional = [
    {"nama": "Senin",  "buka": True,  "jam_buka": "09.00", "jam_tutup": "22.00"},
    {"nama": "Selasa", "buka": True,  "jam_buka": "09.00", "jam_tutup": "22.00"},
    {"nama": "Rabu",   "buka": True,  "jam_buka": "09.00", "jam_tutup": "22.00"},
    {"nama": "Kamis",  "buka": True,  "jam_buka": "09.00", "jam_tutup": "22.00"},
    {"nama": "Jumat",  "buka": True,  "jam_buka": "09.00", "jam_tutup": "22.00"},
    {"nama": "Sabtu",  "buka": True,  "jam_buka": "09.00", "jam_tutup": "22.00"},
    {"nama": "Minggu", "buka": False, "jam_buka": "10.00", "jam_tutup": "20.00"},
]

staff_data = [
    {"id": 1, "nama": "Andi Pratama", "shift": "Pagi",  "status": "online",  "total_transaksi": 42},
    {"id": 2, "nama": "Budi Santoso", "shift": "Sore",  "status": "offline", "total_transaksi": 0},
]

kasir_data = [
    {"id": 1, "nama": "Dimas",   "total_transaksi": 7,  "total_penjualan": 350000, "status": "online"},
    {"id": 2, "nama": "Bg Ari",  "total_transaksi": 3,  "total_penjualan": 100000, "status": "offline"},
    {"id": 3, "nama": "Kak Aca", "total_transaksi": 15, "total_penjualan": 750000, "status": "online"},
]

menu_data = [
    {"id": 1,  "nama": "Ayam Geprek",    "kategori": "Food",       "harga": 20000, "status": True,  "stok": 13},
    {"id": 2,  "nama": "Indomie Kuah",   "kategori": "Food",       "harga": 12000, "status": True,  "stok": 30},
    {"id": 3,  "nama": "Indomie Goreng", "kategori": "Food",       "harga": 12000, "status": True,  "stok": 30},
    {"id": 4,  "nama": "Kentang Goreng", "kategori": "Snack",      "harga": 15000, "status": True,  "stok": 8},
    {"id": 5,  "nama": "Nasi Goreng",    "kategori": "Food",       "harga": 20000, "status": True,  "stok": 12},
    {"id": 6,  "nama": "Matcha",         "kategori": "Non Coffee", "harga": 17000, "status": True,  "stok": 18},
    {"id": 7,  "nama": "Americano",      "kategori": "Coffee",     "harga": 15000, "status": True,  "stok": 25},
    {"id": 8,  "nama": "Dimsum",         "kategori": "Snack",      "harga": 15000, "status": False, "stok": 0},
    {"id": 9,  "nama": "Vanilla Latte",  "kategori": "Non Coffee", "harga": 18000, "status": True,  "stok": 17},
    {"id": 10, "nama": "Beef Teriyaki",  "kategori": "Food",       "harga": 30000, "status": True,  "stok": 7},
]

transaksi_data = [
    {"id_transaksi": "#TRX001", "tanggal": "06 Apr, 14:00:21", "metode": "QRIS",  "total": "Rp45.000"},
    {"id_transaksi": "#TRX002", "tanggal": "06 Apr, 14:00:21", "metode": "QRIS",  "total": "Rp45.000"},
    {"id_transaksi": "#TRX003", "tanggal": "06 Apr, 14:00:21", "metode": "QRIS",  "total": "Rp45.000"},
    {"id_transaksi": "#TRX004", "tanggal": "06 Apr, 13:45:10", "metode": "Cash",  "total": "Rp32.000"},
    {"id_transaksi": "#TRX005", "tanggal": "06 Apr, 13:20:05", "metode": "QRIS",  "total": "Rp58.000"},
    {"id_transaksi": "#TRX006", "tanggal": "06 Apr, 12:55:33", "metode": "Cash",  "total": "Rp27.000"},
    {"id_transaksi": "#TRX007", "tanggal": "06 Apr, 12:10:47", "metode": "Debit", "total": "Rp75.000"},
]

@owner_bp.route('/manajemen-menu')
def manajemen_menu():
    return render_template('owner/manajemen-menu.html', username="Oscar", menu_list=menu_data)

@owner_bp.route('/manajemen-kasir')
def manajemen_kasir():
    kasir_online = sum(1 for k in kasir_data if k['status'] == 'online')
    return render_template('owner/manajemen-kasir.html',
        username="Oscar", kasir_list=kasir_data,
        kasir_online=kasir_online, total_kasir=len(kasir_data)
    )

@owner_bp.route('/laporan-penjualan')
def laporan_penjualan():
    return render_template('owner/laporan-penjualan.html', username="Oscar", transaksi_list=transaksi_data)

@owner_bp.route('/pengaturan')
def pengaturan():
    return render_template('owner/pengaturan.html',
        username="Oscar",
        profil_cafe=profil_cafe,
        akun_owner=akun_owner,
        jam_operasional=jam_operasional
    )

# ── Menu APIs ─────────────────────────────────────────
@owner_bp.route('/api/tambah-menu', methods=['POST'])
def tambah_menu():
    data = request.json
    menu_data.append({
        "id": len(menu_data) + 1, "nama": data.get("nama"),
        "kategori": data.get("kategori"), "harga": int(data.get("harga") or 0),
        "status": True, "stok": int(data.get("stok") or 0),
    })
    return jsonify({"success": True, "message": "Menu baru berhasil ditambahkan!"})

@owner_bp.route('/api/toggle-menu-status/<int:menu_id>', methods=['POST'])
def toggle_menu_status(menu_id):
    data = request.json
    for m in menu_data:
        if m["id"] == menu_id:
            m["status"] = data.get("status"); break
    return jsonify({"success": True, "message": "Status menu diperbarui!"})

# ── Kasir APIs ────────────────────────────────────────
@owner_bp.route('/api/tambah-staff', methods=['POST'])
def tambah_staff():
    data = request.json
    new_id = len(kasir_data) + 1
    kasir_data.append({"id": new_id, "nama": data.get("nama"),
        "total_transaksi": 0, "total_penjualan": 0, "status": "offline"})
    staff_data.append({"id": new_id, "nama": data.get("nama"),
        "shift": "Pagi", "status": "offline", "total_transaksi": 0})
    return jsonify({"success": True, "message": "Staff baru berhasil ditambahkan!"})

@owner_bp.route('/api/toggle-kasir-status/<int:kasir_id>', methods=['POST'])
def toggle_kasir_status(kasir_id):
    data = request.json
    for k in kasir_data:
        if k["id"] == kasir_id:
            k["status"] = data.get("status"); break
    return jsonify({"success": True, "message": "Status kasir diperbarui!"})

@owner_bp.route('/api/edit-kasir/<int:kasir_id>', methods=['POST'])
def edit_kasir(kasir_id):
    data = request.json
    for k in kasir_data:
        if k["id"] == kasir_id:
            k["nama"] = data.get("nama", k["nama"])
            k["status"] = data.get("status", k["status"]); break
    return jsonify({"success": True, "message": "Profil staf berhasil diedit!"})

# ── Pengaturan APIs ───────────────────────────────────
@owner_bp.route('/api/update-profil-cafe', methods=['POST'])
def update_profil_cafe():
    data = request.json
    profil_cafe.update({
        "nama": data.get("nama", profil_cafe["nama"]),
        "telp": data.get("telp", profil_cafe["telp"]),
        "alamat": data.get("alamat", profil_cafe["alamat"]),
        "email": data.get("email", profil_cafe["email"]),
    })
    return jsonify({"success": True, "message": "Profil cafe berhasil diperbarui!"})

@owner_bp.route('/api/update-akun', methods=['POST'])
def update_akun():
    data = request.json
    akun_owner.update({
        "nama": data.get("nama", akun_owner["nama"]),
        "panggilan": data.get("panggilan", akun_owner["panggilan"]),
        "email": data.get("email", akun_owner["email"]),
        "no_hp": data.get("no_hp", akun_owner["no_hp"]),
    })
    return jsonify({"success": True, "message": "Akun berhasil diperbarui!"})

@owner_bp.route('/api/update-password', methods=['POST'])
def update_password():
    data = request.json
    if not data.get("password_lama"):
        return jsonify({"success": False, "message": "Kata sandi lama salah!"})
    return jsonify({"success": True, "message": "Kata sandi berhasil diperbarui!"})

@owner_bp.route('/api/toggle-jam-operasional', methods=['POST'])
def toggle_jam_operasional():
    data = request.json
    for h in jam_operasional:
        if h["nama"] == data.get("hari"):
            h["buka"] = data.get("buka"); break
    return jsonify({"success": True, "message": "Jadwal diperbarui!"})
