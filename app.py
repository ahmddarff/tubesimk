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

# ==========================================
# REGISTRASI BLUEPRINT (ROUTES)
# ==========================================
# Import blueprint dari folder routes
from routes.auth_routes import auth_bp
from routes.kasir_routes import kasir_bp
from routes.customer_routes import customer_bp
from routes.owner_routes import owner_bp
from routes.koki_routes import koki_bp

# Daftarkan blueprint ke aplikasi Flask
app.register_blueprint(auth_bp)
app.register_blueprint(kasir_bp, url_prefix='/kasir')
app.register_blueprint(customer_bp, url_prefix='/customer')
app.register_blueprint(owner_bp, url_prefix='/owner')
app.register_blueprint(koki_bp, url_prefix='/koki')

print(app.url_map)

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


@app.route('/customer/checkout')
def customer_checkout():
    return render_template('customer/checkout.html', segment='checkout', role='customer')


@app.route('/customer/profil')
def customer_profil():
    # Data profil user (nantinya dari database)
    profil_data = {
        'username': 'Matthew Shen',
        'nama_lengkap': 'Matthew Shen',
        'email': 'matthewmoo67@gmail.com',
        'nomor_telepon': '',
    }
    return render_template('customer/profil.html', segment='profil', role='customer', profil=profil_data)


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


@app.route('/customer/reservasi/new')
def customer_buat_reservasi_baru():
    return render_template('customer/buat_reservasi_new.html', segment='buat_reservasi', role='customer')


@app.route('/customer/reservasi/<reservation_id>')
def customer_reservasi_detail(reservation_id):
    return render_template('customer/reservasi_detail.html',
                         segment='buat_reservasi',
                         role='customer',
                         reservation_id=reservation_id)


@app.route('/customer/reservasi/history')
def customer_reservasi_history():
    # Semua Riwayat Reservasi
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
        },
        {
            "id": "AB456",
            "status": "Selesai",
            "date": "15 Maret 2026",
            "time": "19:30 WIB",
            "duration": "3 Jam",
            "guests": "5"
        }
    ]
    
    return render_template('customer/reservasi_history.html',
                         segment='buat_reservasi',
                         role='customer',
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


@app.route('/customer/pesanan/<order_id>')
def customer_pesanan_detail(order_id):
    return render_template('customer/pesanan_aktif_detail.html', 
                         segment='pesanan_saya',
                         role='customer',
                         order_id=order_id)


staff_data = [
    {"id": 1, "nama": "Andi Pratama", "shift": "Pagi", "status": "online", "total_transaksi": 42},
    {"id": 2, "nama": "Budi Santoso", "shift": "Sore", "status": "offline", "total_transaksi": 0},
]

menu_data = []

@app.route('/')
def home():
    # Karena root web biasanya langsung ke login, kita redirect menggunakan nama fungsi di dalam blueprint
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, port=50001)