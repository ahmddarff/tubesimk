import os
from flask import Flask, render_template, jsonify, request, redirect
from extensions import db
from dotenv import load_dotenv

load_dotenv() 

app = Flask(__name__)

# ==========================================
# KONFIGURASI DATABASE (HANYA APP URI)
# ==========================================
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_DATABASE")
APP_USER = os.getenv("DB_APP_USERNAME")
APP_PASS = os.getenv("DB_APP_PASSWORD")

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{APP_USER}:{APP_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

db.init_app(app)

from models import *

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # TODO: Tambahkan validasi username dan password dari database
        # return redirect('/kasir') atau return redirect('/customer')
        pass
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # TODO: Validasi
        # - Cek password == confirm_password
        # - Cek username belum terdaftar
        # - Cek email belum terdaftar
        # - Hash password
        # - Simpan ke database
        # return redirect('/login') dengan pesan sukses
        pass
    return render_template('register.html')

@app.route('/kasir')
def kasir_dashboard():
    katalog_menu = [
        {"nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "rating": 4.7, "terjual": 11, "status": "tersedia"},
        {"nama": "Espresso", "harga": 10000, "img": "kopi.png", "rating": 4.8, "terjual": 5, "status": "tersedia"},
        {"nama": "Sanger", "harga": 18000, "img": "kopi.png", "rating": 4.6, "terjual": 4, "status": "tersedia"},
        {"nama": "Americano", "harga": 15000, "img": "kopi.png", "rating": 4.3, "terjual": 8, "status": "tersedia"},
        {"nama": "Cappuccino", "harga": 18000, "img": "kopi.png", "rating": 4.5, "terjual": 5, "status": "tersedia"},
        {"nama": "Kopi Latte", "harga": 16000, "img": "kopi.png", "rating": 4.3, "terjual": 4, "status": "habis"},
        {"nama": "Americano", "harga": 15000, "img": "kopi.png", "rating": 4.3, "terjual": 8, "status": "tersedia"},
        {"nama": "Cappuccino", "harga": 18000, "img": "kopi.png", "rating": 4.5, "terjual": 5, "status": "tersedia"},
        {"nama": "Kopi Latte", "harga": 16000, "img": "kopi.png", "rating": 4.3, "terjual": 4, "status": "habis"},
    ]
    return render_template('kasir/dashboard.html', menu=katalog_menu, segment='dashboard', role='kasir')
    

@app.route('/pesanan-aktif')
def pesanan_aktif():
    # Data contoh untuk pesanan
    pesanan_list = [
        {"id": "P052", "nama": "Agnes", "meja": "07", "status": "PENDING", "total": 48000, "waktu": "12.12", "tipe": "DINE IN"},
        {"id": "P051", "nama": "Joy", "meja": "-", "status": "PENDING", "total": 48000, "waktu": "11.56", "tipe": "TAKE AWAY"},
        {"id": "P049", "nama": "Rahma", "meja": "06", "status": "READY", "total": 48000, "waktu": "11.27", "tipe": "DINE IN"},
        {"id": "P045", "nama": "Sonya", "meja": "03", "status": "SERVED", "total": 48000, "waktu": "10.40", "tipe": "DINE IN"},
        {"id": "P051", "nama": "Joy", "meja": "-", "status": "PENDING", "total": 48000, "waktu": "11.56", "tipe": "TAKE AWAY"},
        {"id": "P049", "nama": "Rahma", "meja": "06", "status": "READY", "total": 48000, "waktu": "11.27", "tipe": "DINE IN"},
        {"id": "P045", "nama": "Sonya", "meja": "03", "status": "SERVED", "total": 48000, "waktu": "10.40", "tipe": "DINE IN"},
        
    ]
    return render_template('kasir/pesanan_aktif.html', segment='pesanan_aktif', role='kasir', pesanan=pesanan_list)
    
    
@app.route('/reservasi')
def reservasi():
    data_reservasi = [
        {'id': '01', 'nama': 'Richard Lim', 'tanggal': '06/04/2024', 'tamu': 2, 'telepon': '0812345678', 'waktu': '19.00', 'status': 'Menunggu'},
    ]
    return render_template('kasir/reservasi.html', segment='reservasi', role='kasir', reservations=data_reservasi)

@app.route('/riwayat-transaksi')
def riwayat_transaksi():
    stats_data = {
        'total_transaksi': 6,
        'total_penjualan': 450000,
        'tunai_persen': 50,
        'qris_persen': 50
    }

    transaksi_list = [
    {
        'id': 'TRX-00015', 
        'tanggal': '2024-04-06', 
        'waktu': '19.00',
        'pelanggan': 'Richard Lim', 
        'kasir': 'Rahma',
        'metode': 'TUNAI', 
        'total': 50000,
        'items': [{'nama': 'Chicken Katsu', 'harga': 50000, 'jumlah': 1, 'subtotal': 50000}]
    },
    {
        'id': 'TRX-00016', 
        'tanggal': '2024-04-06', 
        'waktu': '19.15',
        'pelanggan': 'Arialdi Manday', 
        'kasir': 'Rahma',
        'metode': 'QRIS', 
        'total': 75000,
        'items': [
            {'nama': 'Terralog Coffee', 'harga': 25000, 'jumlah': 2, 'subtotal': 50000},
            {'nama': 'French Fries', 'harga': 25000, 'jumlah': 1, 'subtotal': 25000}
        ]
    },
    {
        'id': 'TRX-00017', 
        'tanggal': '2024-04-06', 
        'waktu': '19.45',
        'pelanggan': 'Chaterine Jelek', 
        'kasir': 'Rahma',
        'metode': 'TUNAI', 
        'total': 35000,
        'items': [{'nama': 'Matcha Latte', 'harga': 35000, 'jumlah': 1, 'subtotal': 35000}]
    },
    {
        'id': 'TRX-00018', 
        'tanggal': '2024-04-07', 
        'waktu': '10.00',
        'pelanggan': 'Aldrik Running', 
        'kasir': 'Dimas',
        'metode': 'QRIS', 
        'total': 120000,
        'items': [
            {'nama': 'Beef Burger', 'harga': 45000, 'jumlah': 2, 'subtotal': 90000},
            {'nama': 'Lemon Tea', 'harga': 15000, 'jumlah': 2, 'subtotal': 30000}
        ]
    },
    {
        'id': 'TRX-00019', 
        'tanggal': '2024-04-07', 
        'waktu': '11.30',
        'pelanggan': 'Rahmaini Erna', 
        'kasir': 'Dimas',
        'metode': 'TUNAI', 
        'total': 25000,
        'items': [{'nama': 'Americano', 'harga': 25000, 'jumlah': 1, 'subtotal': 25000}]
    },
    {
        'id': 'TRX-00020', 
        'tanggal': '2024-04-07', 
        'waktu': '13.10',
        'pelanggan': 'Earlin Pinky', 
        'kasir': 'Dimas',
        'metode': 'QRIS', 
        'total': 85000,
        'items': [
            {'nama': 'Nasi Goreng Terralog', 'harga': 40000, 'jumlah': 1, 'subtotal': 40000},
            {'nama': 'Caramel Macchiato', 'harga': 45000, 'jumlah': 1, 'subtotal': 45000}
        ]
    },
    {
        'id': 'TRX-00021', 
        'tanggal': '2024-04-08', 
        'waktu': '15.20',
        'pelanggan': 'Budi Santoso', 
        'kasir': 'Rahma',
        'metode': 'TUNAI', 
        'total': 60000,
        'items': [{'nama': 'Spaghetti Carbonara', 'harga': 60000, 'jumlah': 1, 'subtotal': 60000}]
    },
    {
        'id': 'TRX-00022', 
        'tanggal': '2024-04-08', 
        'waktu': '16.00',
        'pelanggan': 'Siti Aminah', 
        'kasir': 'Rahma',
        'metode': 'QRIS', 
        'total': 40000,
        'items': [{'nama': 'Croissant Almond', 'harga': 40000, 'jumlah': 1, 'subtotal': 40000}]
    },
    {
        'id': 'TRX-00023', 
        'tanggal': '2024-04-08', 
        'waktu': '18.45',
        'pelanggan': 'Andi Wijaya', 
        'kasir': 'Rahma',
        'metode': 'TUNAI', 
        'total': 110000,
        'items': [
            {'nama': 'Double Espresso', 'harga': 30000, 'jumlah': 2, 'subtotal': 60000},
            {'nama': 'Club Sandwich', 'harga': 50000, 'jumlah': 1, 'subtotal': 50000}
        ]
    },
    {
        'id': 'TRX-00024', 
        'tanggal': '2024-04-09', 
        'waktu': '09.15',
        'pelanggan': 'Dewi Lestari', 
        'kasir': 'Dimas',
        'metode': 'QRIS', 
        'total': 55000,
        'items': [
            {'nama': 'Caffé Latte', 'harga': 35000, 'jumlah': 1, 'subtotal': 35000},
            {'nama': 'Donut Glaze', 'harga': 20000, 'jumlah': 1, 'subtotal': 20000}
        ]
    }
]
    return render_template('kasir/riwayat_transaksi.html', segment='riwayat_transaksi', stats=stats_data, transactions=transaksi_list, role='kasir')

@app.route('/customer')
def customer_beranda():
    return render_template('customer/beranda.html', segment='customer', role='customer')


@app.route('/customer/daftar-menu')
def customer_daftar_menu():
    # Katalog Menu dengan kategori
    katalog_menu = [
        # Coffee
        {"nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "rating": 4.7, "terjual": 11, "status": "tersedia", "kategori": "coffee"},
        {"nama": "Espresso", "harga": 10000, "img": "kopi.png", "rating": 4.8, "terjual": 5, "status": "tersedia", "kategori": "coffee"},
        {"nama": "Sanger", "harga": 18000, "img": "kopi.png", "rating": 4.6, "terjual": 4, "status": "tersedia", "kategori": "coffee"},
        {"nama": "Americano", "harga": 15000, "img": "kopi.png", "rating": 4.3, "terjual": 8, "status": "tersedia", "kategori": "coffee"},
        {"nama": "Cappuccino", "harga": 18000, "img": "kopi.png", "rating": 4.5, "terjual": 5, "status": "tersedia", "kategori": "coffee"},
        {"nama": "Kopi Latte", "harga": 16000, "img": "kopi.png", "rating": 4.3, "terjual": 4, "status": "habis", "kategori": "coffee"},
        {"nama": "Butter Coffee", "harga": 20000, "img": "kopi.png", "rating": 4.4, "terjual": 7, "status": "tersedia", "kategori": "coffee"},
        {"nama": "Tiramisu Coffee", "harga": 19000, "img": "kopi.png", "rating": 4.6, "terjual": 6, "status": "tersedia", "kategori": "coffee"},
        
        # Non Coffee
        {"nama": "Milk Tea", "harga": 16000, "img": "tea.png", "rating": 4.5, "terjual": 9, "status": "tersedia", "kategori": "noncoffee"},
        {"nama": "Iced Tea", "harga": 12000, "img": "tea.png", "rating": 4.4, "terjual": 8, "status": "tersedia", "kategori": "noncoffee"},
        {"nama": "Chocolate Drink", "harga": 14000, "img": "drink.png", "rating": 4.6, "terjual": 10, "status": "tersedia", "kategori": "noncoffee"},
        
        # Food
        {"nama": "Croissant", "harga": 22000, "img": "food.png", "rating": 4.7, "terjual": 15, "status": "tersedia", "kategori": "food"},
        {"nama": "Sandwich", "harga": 25000, "img": "food.png", "rating": 4.5, "terjual": 12, "status": "tersedia", "kategori": "food"},
        {"nama": "Pasta", "harga": 35000, "img": "food.png", "rating": 4.6, "terjual": 8, "status": "tersedia", "kategori": "food"},
        
        # Snack
        {"nama": "Cookies", "harga": 8000, "img": "snack.png", "rating": 4.4, "terjual": 20, "status": "tersedia", "kategori": "snack"},
        {"nama": "Donut", "harga": 10000, "img": "snack.png", "rating": 4.5, "terjual": 18, "status": "tersedia", "kategori": "snack"},
        {"nama": "Muffin", "harga": 12000, "img": "snack.png", "rating": 4.3, "terjual": 14, "status": "tersedia", "kategori": "snack"},
    ]
    return render_template('customer/daftar_menu.html', menu=katalog_menu, segment='daftar_menu', role='customer')


@app.route('/customer/buat-reservasi')
def customer_buat_reservasi():
    # Reservasi Aktif
    active_reservations = [
        {
            "id": "AB123",
            "status": "Menunggu",
            "date": "06 April 2026",
            "time": "15:15 WIB",
            "duration": "2 Jam",
            "guests": "21"
        }
    ]
    
    # Riwayat Reservasi
    history_reservations = [
        {
            "id": "AB650",
            "status": "Selesai",
            "date": "05 April 2026",
            "time": "16:00 WIB",
            "duration": "1 Jam",
            "guests": "2"
        },
        {
            "id": "AC780",
            "status": "Dibatalkan",
            "date": "06 Desember 2025",
            "time": "08:00 WIB",
            "duration": "2+ Jam",
            "guests": "134"
        }
    ]
    
    return render_template('customer/buat_reservasi.html',
                         segment='buat_reservasi',
                         role='customer',
                         active_reservations=active_reservations,
                         history_reservations=history_reservations)


@app.route('/customer/pesanan-saya')
def customer_pesanan_saya():
    # Pesanan Aktif
    active_orders = [
        {
            "id": "AB123",
            "status": "Hidangkan",
            "date": "06 April 2026",
            "time": "15:15 WIB",
            "products": [
                {"nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "qty": 2}
            ],
            "total": 43000
        }
    ]
    
    # Riwayat Pesanan
    history_orders = [
        {
            "id": "AB098",
            "status": "Selesai",
            "date": "14 Februari 2026",
            "time": "21:48 WIB",
            "products": [
                {"nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "qty": 2}
            ],
            "total": 38000
        },
        {
            "id": "AB073",
            "status": "Dibatalkan",
            "date": "13 Januari 2026",
            "time": "17:45 WIB",
            "products": [
                {"nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "qty": 1}
            ],
            "total": 18000
        }
    ]
    
    return render_template('customer/pesanan_saya.html', 
                         segment='pesanan_saya',
                         role='customer',
                         active_orders=active_orders,
                         history_orders=history_orders)

staff_data = [
    {"id": 1, "nama": "Andi Pratama", "shift": "Pagi", "status": "online", "total_transaksi": 42},
    {"id": 2, "nama": "Budi Santoso", "shift": "Sore", "status": "offline", "total_transaksi": 0},
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
]

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('owner/dashboard.html',
        username="Oscar",
        total_penjualan="Rp2.500.000,00",
        total_order=124,
        menu_terlaris="Caramel Latte",
        menu_terlaris_qty=45,
        staff=staff_data
    )

@app.route('/manajemen-menu')
def manajemen_menu():
    return render_template('owner/manajemen-menu.html', username="Oscar", menu_list=menu_data)

@app.route('/manajemen-kasir')
def manajemen_kasir():
    kasir_online = sum(1 for k in kasir_data if k['status'] == 'online')
    return render_template('owner/manajemen-kasir.html',
        username="Oscar",
        kasir_list=kasir_data,
        kasir_online=kasir_online,
        total_kasir=len(kasir_data)
    )

@app.route('/laporan-penjualan')
def laporan_penjualan():
    return render_template('owner/laporan-penjualan.html',
        username="Oscar",
        transaksi_list=transaksi_data
    )

@app.route('/pengaturan')
def pengaturan():
    return render_template('owner/pengaturan.html', username="Oscar")

# ── Menu APIs ──────────────────────────────────────────
@app.route('/api/tambah-menu', methods=['POST'])
def tambah_menu():
    data = request.json
    menu_data.append({
        "id":       len(menu_data) + 1,
        "nama":     data.get("nama"),
        "kategori": data.get("kategori"),
        "harga":    int(data.get("harga") or 0),
        "status":   True,
        "stok":     int(data.get("stok") or 0),
    })
    return jsonify({"success": True, "message": "Menu baru berhasil ditambahkan!"})

@app.route('/api/toggle-menu-status/<int:menu_id>', methods=['POST'])
def toggle_menu_status(menu_id):
    data = request.json
    for m in menu_data:
        if m["id"] == menu_id:
            m["status"] = data.get("status", m["status"])
            break
    return jsonify({"success": True, "message": "Status menu diperbarui!"})

# ── Kasir APIs ─────────────────────────────────────────
@app.route('/api/tambah-staff', methods=['POST'])
def tambah_staff():
    data = request.json
    new_id = len(kasir_data) + 1
    kasir_data.append({
        "id":               new_id,
        "nama":             data.get("nama"),
        "total_transaksi":  0,
        "total_penjualan":  0,
        "status":           "offline"
    })
    staff_data.append({
        "id":               new_id,
        "nama":             data.get("nama"),
        "shift":            "Pagi",
        "status":           "offline",
        "total_transaksi":  0
    })
    return jsonify({"success": True, "message": "Staff baru berhasil ditambahkan!"})

@app.route('/api/toggle-kasir-status/<int:kasir_id>', methods=['POST'])
def toggle_kasir_status(kasir_id):
    data = request.json
    for k in kasir_data:
        if k["id"] == kasir_id:
            k["status"] = data.get("status", k["status"])
            break
    return jsonify({"success": True, "message": "Status kasir diperbarui!"})

@app.route('/api/edit-kasir/<int:kasir_id>', methods=['POST'])
def edit_kasir(kasir_id):
    data = request.json
    for k in kasir_data:
        if k["id"] == kasir_id:
            k["nama"]   = data.get("nama", k["nama"])
            k["status"] = data.get("status", k["status"])
            break
    return jsonify({"success": True, "message": "Profil staf berhasil diedit!"})

if __name__ == '__main__':
    app.run(debug=True, port=50001)