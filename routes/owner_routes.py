from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user 
from models import User, CafeSetting, OperationalHour, Menu, Category
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

owner_bp = Blueprint('owner', __name__)

@owner_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('owner/dashboard.html')

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
@login_required
def manajemen_menu():
    # Ambil semua data menu dan kategori dari database
    menus = Menu.query.all()
    categories = Category.query.all()
    return render_template('owner/manajemen-menu.html',
                           menu_list=menus, 
                           categories=categories)

@owner_bp.route('/manajemen-kasir')
@login_required
def manajemen_kasir():
    kasir_online = sum(1 for k in kasir_data if k['status'] == 'online')
    return render_template('owner/manajemen-kasir.html',
        kasir_list=kasir_data,
        kasir_online=kasir_online, 
        total_kasir=len(kasir_data)
    )

@owner_bp.route('/laporan-penjualan')
@login_required
def laporan_penjualan():
    return render_template('owner/laporan-penjualan.html',
        transaksi_list=transaksi_data
    )

@owner_bp.route('/pengaturan')
@login_required
def pengaturan():
    cafe_info = CafeSetting.query.first()
    
    # Ambil dan urutkan jadwal
    jam_db = OperationalHour.query.all()
    urutan_hari = {"Senin": 1, "Selasa": 2, "Rabu": 3, "Kamis": 4, "Jumat": 5, "Sabtu": 6, "Minggu": 7}
    jam_db.sort(key=lambda x: urutan_hari.get(x.day_of_week, 8))

    # Lempar objeknya langsung! Tidak perlu dictionary data_cafe
    return render_template('owner/pengaturan.html',
        cafe_info=cafe_info,
        jam_operasional=jam_db
    )

# ── Menu APIs ─────────────────────────────────────────
@owner_bp.route('/api/tambah-menu', methods=['POST'])
@login_required
def tambah_menu():
    data = request.json
    # Cari kategori berdasarkan nama yang dikirim dari form
    category = Category.query.filter_by(name=data.get("kategori")).first()
    
    if not category:
        return jsonify({"success": False, "message": "Kategori tidak ditemukan."})

    new_menu = Menu(
        name=data.get("nama"),
        category_id=category.id,
        price=int(data.get("harga") or 0),
        description=data.get("deskripsi"),
        is_available=True
    )
    
    try:
        db.session.add(new_menu)
        db.session.commit()
        return jsonify({"success": True, "message": "Menu baru berhasil ditambahkan!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Gagal menambahkan menu."})

@owner_bp.route('/api/toggle-menu-status/<int:menu_id>', methods=['POST'])
@login_required
def toggle_menu_status(menu_id):
    data = request.json
    # Gunakan db.session.get untuk menghindari LegacyAPIWarning
    menu = db.session.get(Menu, menu_id)
    if menu:
        menu.is_available = data.get("status")
        try:
            db.session.commit()
            return jsonify({"success": True, "message": "Status menu diperbarui!"})
        except:
            db.session.rollback()
            return jsonify({"success": False, "message": "Gagal memperbarui status."})
    return jsonify({"success": False, "message": "Menu tidak ditemukan."})

# ── Kasir APIs ────────────────────────────────────────
@owner_bp.route('/api/tambah-staff', methods=['POST'])
@login_required
def tambah_staff():
    data = request.json
    new_id = len(kasir_data) + 1
    kasir_data.append({"id": new_id, "nama": data.get("nama"),
        "total_transaksi": 0, "total_penjualan": 0, "status": "offline"})
    staff_data.append({"id": new_id, "nama": data.get("nama"),
        "shift": "Pagi", "status": "offline", "total_transaksi": 0})
    return jsonify({"success": True, "message": "Staff baru berhasil ditambahkan!"})

@owner_bp.route('/api/toggle-kasir-status/<int:kasir_id>', methods=['POST'])
@login_required
def toggle_kasir_status(kasir_id):
    data = request.json
    for k in kasir_data:
        if k["id"] == kasir_id:
            k["status"] = data.get("status"); break
    return jsonify({"success": True, "message": "Status kasir diperbarui!"})

@owner_bp.route('/api/edit-kasir/<int:kasir_id>', methods=['POST'])
@login_required
def edit_kasir(kasir_id):
    data = request.json
    for k in kasir_data:
        if k["id"] == kasir_id:
            k["nama"] = data.get("nama", k["nama"])
            k["status"] = data.get("status", k["status"]); break
    return jsonify({"success": True, "message": "Profil staf berhasil diedit!"})

# ── Pengaturan APIs ───────────────────────────────────
@owner_bp.route('/api/update-profil-cafe', methods=['POST'])
@login_required
def update_profil_cafe():
    data = request.json
    
    # Ambil baris pertama dari tabel pengaturan cafe
    cafe_info = CafeSetting.query.first()
    
    if cafe_info:
        # Timpa data lama dengan data baru dari form frontend
        cafe_info.cafe_name = data.get("nama", cafe_info.cafe_name)
        cafe_info.phone = data.get("telp", cafe_info.phone)
        cafe_info.address = data.get("alamat", cafe_info.address)
        cafe_info.email = data.get("email", cafe_info.email)
        
        try:
            db.session.commit()
            return jsonify({"success": True, "message": "Profil cafe berhasil diperbarui di database!"})
        except Exception as e:
            db.session.rollback()
            print(f"Error update cafe: {e}")
            return jsonify({"success": False, "message": "Gagal menyimpan ke database."})
            
    return jsonify({"success": False, "message": "Data pengaturan cafe tidak ditemukan di sistem."})

@owner_bp.route('/api/update-akun', methods=['POST'])
@login_required
def update_akun():
    data = request.json
    
    # Ambil user dari database berdasarkan ID current_user
    user = User.query.get(current_user.id)
    
    if user:
        user.name = data.get("nama", user.name)
        user.username = data.get("username", user.username) # Pastikan field ini ada di form
        user.email = data.get("email", user.email)
        user.phone = data.get("no_hp", user.phone)
        
        try:
            db.session.commit()
            return jsonify({"success": True, "message": "Akun berhasil diperbarui di database!"})
        except Exception as e:
            db.session.rollback()
            print(f"Error updating user: {e}")
            return jsonify({"success": False, "message": "Gagal memperbarui database."})
            
    return jsonify({"success": False, "message": "Pengguna tidak ditemukan."})

@owner_bp.route('/api/update-password', methods=['POST'])
@login_required
def update_password():
    data = request.json
    password_lama = data.get("password_lama")
    password_baru = data.get("password_baru")
    
    user = User.query.get(current_user.id)
    
    # Verifikasi kata sandi lama
    if not check_password_hash(user.password, password_lama):
        return jsonify({"success": False, "message": "Kata sandi lama salah!"})
    
    # Enkripsi kata sandi baru
    user.password = generate_password_hash(password_baru)
    
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Kata sandi berhasil diperbarui!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Gagal menyimpan kata sandi baru."})

@owner_bp.route('/api/update-waktu-operasional', methods=['POST'])
@login_required
def update_waktu_operasional():
    data = request.json
    hari = data.get("hari")
    jenis = data.get("jenis") # Akan berisi 'buka' atau 'tutup'
    waktu_str = data.get("waktu") # Akan berisi string seperti '09:00'
    
    # Cari jadwal hari tersebut di database
    jadwal = OperationalHour.query.filter_by(day_of_week=hari).first()
    
    if jadwal and waktu_str:
        # Konversi string jam 'HH:MM' dari HTML menjadi objek Time Python
        waktu_obj = datetime.strptime(waktu_str, '%H:%M').time()
        
        # Tentukan apakah yang diubah jam buka atau jam tutup
        if jenis == 'buka':
            jadwal.open_time = waktu_obj
        elif jenis == 'tutup':
            jadwal.close_time = waktu_obj
            
        try:
            db.session.commit()
            return jsonify({"success": True, "message": "Waktu berhasil diperbarui!"})
        except Exception as e:
            db.session.rollback()
            print(f"Error update waktu: {e}")
            return jsonify({"success": False, "message": "Gagal menyimpan ke database."})
            
    return jsonify({"success": False, "message": "Jadwal atau data waktu tidak valid!"})
