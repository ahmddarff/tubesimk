from datetime import time, date, datetime
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, CafeSetting, OperationalHour, Category, Menu, Order, OrderItem, Table, Reservation, ReservationTable

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
                logo="terralog.jpeg",
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
                username='owner',
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
                username='kasir',
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
                username='customer',
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

        # ==========================================
        # 8. SEEDER MEJA (TABLE) 
        # ==========================================
        data_meja = [
            {"nomor": "01", "kapasitas": 4, "tersedia": False}, # Sedang dipakai
            {"nomor": "02", "kapasitas": 2, "tersedia": False}, # Sedang dipakai
            {"nomor": "03", "kapasitas": 4, "tersedia": True},  # Kosong
            {"nomor": "04", "kapasitas": 6, "tersedia": False}, # Sedang dipakai
            {"nomor": "05", "kapasitas": 2, "tersedia": True}   # Kosong
        ]
        
        # Dictionary untuk menyimpan ID meja yang baru dibuat agar mudah dipanggil oleh Order
        meja_db = {}
        for meja in data_meja:
            m = Table.query.filter_by(table_number=meja["nomor"]).first()
            if not m:
                m = Table(
                    table_number=meja["nomor"],
                    capacity=meja["kapasitas"],
                    is_available=meja["tersedia"]
                )
                db.session.add(m)
                db.session.commit()
            meja_db[meja["nomor"]] = m.id
            
        print("✅ Berhasil: 5 Data Meja ditambahkan!")

       # ==========================================
        # 9. SEEDER ORDER & ORDER ITEMS 
        # ==========================================
        # Mengambil referensi pelanggan dan menu dari basis data
        customer = User.query.filter_by(role='customer').first()
        customer_id = customer.id if customer else 1
        
        # Mengambil menu_id untuk mengisi order item
        menu_ayam = Menu.query.filter_by(name="Ayam Geprek").first()
        menu_kentang = Menu.query.filter_by(name="Kentang Goreng").first()
        menu_indomie = Menu.query.filter_by(name="Indomie Kuah").first()
        menu_avocado = Menu.query.filter_by(name="Avocado Juice").first()
        menu_dimsum = Menu.query.filter_by(name="Dimsum").first()
        menu_americano = Menu.query.filter_by(name="Americano").first()
        
        # Fallback ID (Cadangan) jika menu di atas terhapus
        fallback_id = Menu.query.first().id if Menu.query.first() else 1

        # Daftar 4 Pesanan dengan waktu (created_at) yang disimulasikan berbeda
        data_orders = [
            {
                "order_number": "ORD-20260514-001",
                "user_id": customer_id,
                "customer_name": None,
                "table_id": meja_db.get("01"),
                "order_type": "dine_in",
                "order_status": "served",
                "payment_method": "cash",
                "payment_status": "paid",
                "total_amount": 50000,
                "created_at": datetime(2026, 5, 14, 10, 0, 0), # Datang pukul 10:00
                "items": [
                    {"menu_id": menu_ayam.id if menu_ayam else fallback_id, "qty": 1, "price": 20000, "notes": "Pedas manis", "status": "served"},
                    {"menu_id": menu_kentang.id if menu_kentang else fallback_id, "qty": 2, "price": 15000, "notes": "Saus pisah", "status": "served"}
                ]
            },
            {
                "order_number": "ORD-20260514-002",
                "user_id": None,
                "customer_name": "Tamu Anonim",
                "table_id": meja_db.get("02"),
                "order_type": "dine_in",
                "order_status": "preparing",
                "payment_method": "qris",
                "payment_status": "paid",
                "total_amount": 29000,
                "created_at": datetime(2026, 5, 14, 10, 15, 0), # Datang pukul 10:15
                "items": [
                    {"menu_id": menu_indomie.id if menu_indomie else fallback_id, "qty": 1, "price": 12000, "notes": "Kuah dikit", "status": "preparing"},
                    {"menu_id": menu_avocado.id if menu_avocado else fallback_id, "qty": 1, "price": 17000, "notes": "No sugar", "status": "pending"}
                ]
            },
            {
                "order_number": "ORD-20260514-003",
                "user_id": customer_id,
                "customer_name": None,
                "table_id": meja_db.get("04"),
                "order_type": "dine_in",
                "order_status": "pending",
                "payment_method": "cash",
                "payment_status": "unpaid",
                "total_amount": 45000,
                "created_at": datetime(2026, 5, 14, 10, 30, 0), # Datang pukul 10:30
                "items": [
                    {"menu_id": menu_dimsum.id if menu_dimsum else fallback_id, "qty": 3, "price": 15000, "notes": "Saus dimsum banyak", "status": "pending"}
                ]
            },
            {
                "order_number": "ORD-20260514-004",
                "user_id": None,
                "customer_name": "Ojol Grab",
                "table_id": None,
                "order_type": "take_away",
                "order_status": "ready",
                "payment_method": "cash",
                "payment_status": "unpaid",
                "total_amount": 30000,
                "created_at": datetime(2026, 5, 14, 10, 45, 0), # Datang pukul 10:45
                "items": [
                    {"menu_id": menu_americano.id if menu_americano else fallback_id, "qty": 1, "price": 15000, "notes": "Less ice", "status": "ready"},
                    {"menu_id": menu_kentang.id if menu_kentang else fallback_id, "qty": 1, "price": 15000, "notes": "Tambahkan sendok", "status": "ready"}
                ]
            }
        ]

        # Proses memasukkan (insert) data Order dan OrderItem ke basis data
        for data in data_orders:
            order_exist = Order.query.filter_by(order_number=data["order_number"]).first()
            if not order_exist:
                # Membuat Pesanan (Order) dengan memasukkan created_at secara spesifik
                pesanan_baru = Order(
                    order_number=data["order_number"],
                    user_id=data["user_id"],
                    customer_name=data["customer_name"],
                    table_id=data["table_id"],
                    order_type=data["order_type"],
                    order_status=data["order_status"],
                    payment_method=data["payment_method"],
                    payment_status=data["payment_status"],
                    total_amount=data["total_amount"],
                    created_at=data["created_at"]  # <-- Injeksi waktu pembuatan di sini
                )
                db.session.add(pesanan_baru)
                db.session.commit() # Disimpan agar pesanan_baru.id terbentuk
                
                # Membuat Detail Item Pesanan (OrderItem)
                for item in data["items"]:
                    item_baru = OrderItem(
                        order_id=pesanan_baru.id,
                        menu_id=item["menu_id"],
                        qty=item["qty"],
                        price_at_order=item["price"],
                        notes=item["notes"],
                        item_status=item["status"]
                    )
                    db.session.add(item_baru)
                    
                db.session.commit()
        print("✅ Berhasil: 4 Data Order (dengan rentang waktu berbeda) dan 7 Data Order Item ditambahkan!")

        # ==========================================
        # 10. SEEDER RESERVASI
        # ==========================================
        customer = User.query.filter_by(role='customer').first()
        customer_id = customer.id if customer else 1
        customer_phone = customer.phone if customer and customer.phone else "081299998888"

        meja_db = {m.table_number: m.id for m in Table.query.all()}
        fallback_table = list(meja_db.values())[0] if meja_db else 1

        data_reservasi = [
            {
                "user_id": customer_id,
                "reservation_number": "RES-20260515-001",
                "customer_name": None,
                "phone": customer_phone,
                "guest_qty": 2, # Kolom Baru
                "duration": 90, # Kolom Baru (menit)
                "tables": [meja_db.get("02", fallback_table)], # Diubah menjadi list untuk mendukung multi-meja
                "notes": None,
                "cancellation_reason": None,
                "reservation_date": date(2026, 5, 15),
                "reservation_time": time(19, 0),
                "status": "pending"
            },
            {
                "user_id": customer_id,
                "reservation_number": "RES-20260515-002",
                "customer_name": None,
                "phone": customer_phone,
                "guest_qty": 4,
                "duration": 120,
                "tables": [meja_db.get("01", fallback_table)],
                "notes": "Tolong siapkan kursi tinggi untuk balita.",
                "cancellation_reason": None,
                "reservation_date": date(2026, 5, 16),
                "reservation_time": time(20, 0),
                "status": "confirmed"
            },
            {
                "user_id": None,
                "reservation_number": "RES-20260514-003",
                "customer_name": "Ibu Ratna",
                "phone": "081999888777",
                "guest_qty": 8,
                "duration": 150,
                "tables": [meja_db.get("03", fallback_table), meja_db.get("04", fallback_table)], # Contoh penggabungan 2 meja
                "notes": "Acara keluarga",
                "cancellation_reason": None,
                "reservation_date": date(2026, 5, 14),
                "reservation_time": time(12, 30),
                "status": "completed"
            }
        ]

        for data in data_reservasi:
            reservasi_exist = Reservation.query.filter_by(
                reservation_number=data["reservation_number"]
            ).first()

            if not reservasi_exist:
                # 1. Simpan data ke tabel Reservation
                reservasi_baru = Reservation(
                    user_id=data["user_id"],
                    reservation_number=data["reservation_number"],
                    customer_name=data["customer_name"],
                    phone=data["phone"],
                    guest_qty=data["guest_qty"],
                    duration=data["duration"],
                    notes=data["notes"],
                    cancellation_reason=data["cancellation_reason"],
                    reservation_date=data["reservation_date"],
                    reservation_time=data["reservation_time"],
                    status=data["status"]
                )
                db.session.add(reservasi_baru)
                db.session.commit() # Dicommit agar mendapatkan reservasi_baru.id
                
                # 2. Simpan relasi meja ke tabel ReservationTable
                for t_id in data["tables"]:
                    table_obj = Table.query.get(t_id)
                    snapshot = table_obj.table_number if table_obj else "Unknown"
                    res_table = ReservationTable(
                        reservation_id=reservasi_baru.id,
                        table_id=t_id,
                        table_number_snapshot=snapshot
                    )
                    db.session.add(res_table)
                db.session.commit()
        
        print("✅ Berhasil: Data Reservasi & Relasi Meja ditambahkan!")
        
        print("--- SEEDER SELESAI ---\n")

# Ini memungkinkan file dijalankan langsung via terminal
if __name__ == '__main__':
    run_seeders()