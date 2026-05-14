from datetime import time
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, CafeSetting, OperationalHour, Category, Menu

def run_seeders():
    # Gunakan app_context agar SQLAlchemy tahu database mana yang dipakai
    with app.app_context():
        print("\n--- MENJALANKAN DATA SEEDER ---")
        
        # ==========================================
        # 1. SEEDER PROFIL CAFE
        # ==========================================
        setting_exist = CafeSetting.query.first()
        
        if not setting_exist:
            new_setting = CafeSetting(
                cafe_name="Terralog Coffee & Eatery",
                phone="+62 812-XXXX-XXXX",
                email="hello@terralog.com",
                address="Jl. Aman I No.2, Teladan Bar., Kec. Medan Kota, Kota Medan, Sumatera Utara 20216",
            )
            db.session.add(new_setting)
            db.session.commit()
            print("✅ Berhasil: Data Profil Cafe awal ditambahkan!")
        else:
            print("ℹ️ Lewati: Data Profil Cafe sudah ada.")

        # ==========================================
        # 2. SEEDER JAM OPERASIONAL (SENIN - MINGGU)
        # ==========================================
        if not OperationalHour.query.first():
            jadwal_awal = [
                {"day": "Senin",  "is_open": True,  "open": time(9, 0), "close": time(22, 0)},
                {"day": "Selasa", "is_open": True,  "open": time(9, 0), "close": time(22, 0)},
                {"day": "Rabu",   "is_open": True,  "open": time(9, 0), "close": time(22, 0)},
                {"day": "Kamis",  "is_open": True,  "open": time(9, 0), "close": time(22, 0)},
                {"day": "Jumat",  "is_open": True,  "open": time(9, 0), "close": time(22, 0)},
                {"day": "Sabtu",  "is_open": True,  "open": time(9, 0), "close": time(22, 0)},
                {"day": "Minggu", "is_open": False, "open": time(10, 0), "close": time(20, 0)}, # Contoh Minggu tutup/buka beda
            ]
            
            for jadwal in jadwal_awal:
                new_hour = OperationalHour(
                    day_of_week=jadwal["day"],
                    is_open=jadwal["is_open"],
                    open_time=jadwal["open"],
                    close_time=jadwal["close"]
                )
                db.session.add(new_hour)
            
            db.session.commit()
            print("✅ Berhasil: Jadwal Operasional (7 Hari) ditambahkan!")
        else:
            print("ℹ️ Lewati: Jadwal Operasional sudah ada.")

        # ==========================================
        # 3. SEEDER AKUN OWNER
        # ==========================================
        owner_exist = User.query.filter_by(role='owner').first()
        
        if not owner_exist:
            hashed_password = generate_password_hash('owner123')
            new_owner = User(
                name='Oscar Piastri',
                username='owner_oscar',
                email='oscar.owner@gmail.com',
                password=hashed_password,
                phone='0812-xxxx-xxxx',
                role='owner',
                is_active=True
            )
            db.session.add(new_owner)
            db.session.commit()
            print("✅ Berhasil: Akun Owner (Oscar Piastri) ditambahkan!")
        else:
            print("ℹ️ Lewati: Akun Owner sudah ada.")

        # ==========================================
        # 4. SEEDER AKUN KASIR
        # ==========================================
        kasir_exist = User.query.filter_by(role='kasir').first()
        
        if not kasir_exist:
            hashed_password = generate_password_hash('kasir123') # Password untuk login
            new_kasir = User(
                name='Zhang Hao',
                username='kasir_hao',
                email='hao.kasir@gmail.com',
                password=hashed_password,
                phone='0813-xxxx-xxxx',
                role='kasir',
                is_active=True
            )
            db.session.add(new_kasir)
            db.session.commit()
            print("✅ Berhasil: Akun Kasir (Zhang Hao) ditambahkan!")
        else:
            print("ℹ️ Lewati: Akun Kasir sudah ada.")

        # ==========================================
        # 5. SEEDER AKUN CUSTOMER
        # ==========================================
        customer_exist = User.query.filter_by(role='customer').first()
        
        if not customer_exist:
            hashed_password = generate_password_hash('customer123') # Password untuk login
            new_customer = User(
                name='Budi Pelanggan',
                username='customer_budi',
                email='budi.customer@gmail.com',
                password=hashed_password,
                phone='0812-9999-8888',
                role='customer',
                is_active=True
            )
            db.session.add(new_customer)
            db.session.commit()
            print("✅ Berhasil: Akun Customer (Budi Pelanggan) ditambahkan!")
        else:
            print("ℹ️ Lewati: Akun Customer sudah ada.")
            
        # ==========================================
        # 6. SEEDER KATEGORI MENU
        # ==========================================
        # Daftar kategori yang dibutuhkan berdasarkan mock data Anda
        daftar_kategori = ['Food', 'Snack', 'Coffee', 'Non Coffee']
        
        for nama_kategori in daftar_kategori:
            kategori_exist = Category.query.filter_by(name=nama_kategori).first()
            if not kategori_exist:
                kategori_baru = Category(name=nama_kategori)
                db.session.add(kategori_baru)
                
        # Commit kategori agar kita bisa mendapatkan ID-nya untuk tabel Menu
        db.session.commit()
        print("✅ Berhasil: Data Kategori dipastikan tersedia!")

        # ==========================================
        # 7. SEEDER MENU
        # ==========================================
        # Mengambil data kategori dari database untuk mendapatkan ID-nya
        kategori_db = {k.name: k.id for k in Category.query.all()}

        # Data menu awal yang akan di-seed
        data_menu = [
            {"nama": "Ayam Geprek", "kategori": "Food", "harga": 20000, "deskripsi": "Ayam geprek pedas dengan sambal bawang", "stok": None, "image_url": "https://thumbs.dreamstime.com/b/ayam-geprek-indonesian-food-crispy-fried-chicken-hot-spicy-sambal-chili-sauce-currently-found-indonesia-215159626.jpg"},
            {"nama": "Indomie Kuah", "kategori": "Food", "harga": 12000, "deskripsi": "Indomie rebus dengan telur dan sayur", "stok": None, "image_url": "https://www.jagel.id/api/listimage/v/IndomieRebus-0-17531161553185a8fcddf4cd3e4.79623077.png"},
            {"nama": "Kentang Goreng", "kategori": "Snack", "harga": 15000, "deskripsi": "Kentang goreng renyah porsi besar", "stok": 50, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTqKffaols_tIAXKilwEuuUOzUKRcoJDvHBLw&s"},
            {"nama": "Americano", "kategori": "Coffee", "harga": 15000, "deskripsi": "Kopi hitam espresso dengan air", "stok": None, "image_url": "https://richcreme.com/wp-content/uploads/2025/02/Americano-2.webp"},
            {"nama": "Avocado Juice", "kategori": "Non Coffee", "harga": 17000, "deskripsi": "Minuman jus alpukat dengan susu segar", "stok": None, "image_url": "https://www.shutterstock.com/image-photo/picture-avocado-honey-smoothie-decorate-600nw-2395659467.jpg"},
            {"nama": "Dimsum", "kategori": "Snack", "harga": 15000, "deskripsi": "Dimsum ayam udang isi 4 pcs", "stok": 20, "image_url": "https://www.shutterstock.com/image-photo/chinese-steamed-shrimp-dimsum-white-260nw-1476920966.jpg"}
        ]

        for item in data_menu:
            menu_exist = Menu.query.filter_by(name=item['nama']).first()
            if not menu_exist:
                menu_baru = Menu(
                    name=item['nama'],
                    category_id=kategori_db[item['kategori']], # Mengambil ID kategori berdasarkan namanya
                    price=item['harga'],
                    description=item['deskripsi'],
                    stock=item['stok'],
                    image_url=item.get('image_url'),
                    is_available=True
                )
                db.session.add(menu_baru)
        
        db.session.commit()
        print("✅ Berhasil: Data Menu ditambahkan!")
        
        print("--- SEEDER SELESAI ---\n")

# Ini memungkinkan file dijalankan langsung via terminal
if __name__ == '__main__':
    run_seeders()