from flask import Flask, render_template
from extensions import db
# pip install sqlalchemy-utils di terminal dulu sebelum pakai ini
from sqlalchemy_utils import database_exists, create_database
# pip install Flask-SQLAlchemy pymysql

app = Flask(__name__)

# ==========================================
# KONFIGURASI DATABASE MYSQL
# ==========================================
# Ganti 'root', password (kosong), dan 'terralog_db' sesuai XAMPP/MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/terralog_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Hubungkan db dengan app
db.init_app(app)

# Import semua class dari models.py agar dikenali saat pembuatan tabel
# Pastikan file models.py yang kita bahas sebelumnya sudah ada sejajar dengan app.py
from models import User, CafeSetting, Category, Menu, Table, Reservation, Order, OrderItem, Review

# Setup database dan tabel secara otomatis saat aplikasi dijalankan
with app.app_context():
    # 1. Cek database 'terralog_db' sudah ada di server MySQL Laragon/XAMPP
    if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        # 2. Jika belum ada, buat baru dengan nama 'terralog_db'
        create_database(app.config['SQLALCHEMY_DATABASE_URI'])
        print("Wadah Database 'terralog_db' berhasil diciptakan otomatis!")
    
    # 3. Setelah wadahnya pasti ada, baru kita buat tabel-tabelnya
    db.create_all()
    print("Mengecek/Membuat tabel Database MySQL selesai!")

@app.route('/')
def home():
    return "Hello Terralog!"

@app.route('/kasir')
def kasir_dashboard():
    katalog_menu = [
        {"nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "rating": 4.7, "terjual": 11, "status": "tersedia"},
        {"nama": "Espresso", "harga": 10000, "img": "kopi.png", "rating": 4.8, "terjual": 5, "status": "tersedia"},
        {"nama": "Sanger", "harga": 18000, "img": "kopi.png", "rating": 4.6, "terjual": 4, "status": "tersedia"},
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

if __name__ == '__main__':
    app.run(debug=True, port=50001)