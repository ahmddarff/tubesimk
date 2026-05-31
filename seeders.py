from datetime import time, date, datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, CafeSetting, OperationalHour, Category, Menu, Order, OrderItem, Table, Reservation, ReservationTable, Review

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
                {"day": "Minggu", "is_open": False, "open": time(10, 0), "close": time(20, 0)},
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
            print("✅ Berhasil: Akun Owner ditambahkan!")
        else:
            print("ℹ️ Lewati: Akun Owner sudah ada.")

        # ==========================================
        # 4. SEEDER AKUN KASIR
        # ==========================================
        kasir_exist = User.query.filter_by(role='kasir').first()
        
        if not kasir_exist:
            hashed_password = generate_password_hash('kasir123')
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
            print("✅ Berhasil: Akun Kasir ditambahkan!")
        else:
            print("ℹ️ Lewati: Akun Kasir sudah ada.")

        # ==========================================
        # 5. SEEDER AKUN KOKI
        # ==========================================
        koki_exist = User.query.filter_by(role='koki').first()
        
        if not koki_exist:
            hashed_password = generate_password_hash('koki123')
            new_koki = User(
                name='Sung Hanbin',
                username='koki',
                email='hanbin.koki@gmail.com',
                password=hashed_password,
                phone='0814-xxxx-xxxx',
                role='koki',
                is_active=True
            )
            db.session.add(new_koki)
            db.session.commit()
            print("✅ Berhasil: Akun Koki Utama ditambahkan!")
        else:
            print("ℹ️ Lewati: Akun Koki Utama sudah ada.")

        # ==========================================
        # 6. SEEDER AKUN CUSTOMER
        # ==========================================
        data_customers = [
            {'name': 'Budi Pelanggan', 'username': 'customer', 'email': 'budi@gmail.com', 'phone': '0812-9999-8888', 'photo': None},
            {'name': 'Shen Ricky', 'username': 'ricky', 'email': 'ricky@gmail.com', 'phone': '0812-1111-2222', 'photo': 'https://i.pinimg.com/736x/3c/12/ae/3c12ae53e5d577d803c80499009a6c2d.jpg'},
            {'name': 'Han Yujin', 'username': 'yujin', 'email': 'yujin@gmail.com', 'phone': '0812-3333-4444', 'photo': 'https://i.pinimg.com/736x/fb/b0/37/fbb037596d2b9f48b624c073e756a64f.jpg'},
            {'name': 'Kim Gyuvin', 'username': 'gyuvin', 'email': 'gyuvin@gmail.com', 'phone': '0812-5555-6666', 'photo': 'https://i.pinimg.com/736x/c0/dd/21/c0dd2130f3cea13b6a2b01e071d9ed4c.jpg'},
            {'name': 'Yoo Seungeon', 'username': 'seungeon', 'email': 'seungeon@gmail.com', 'phone': '0812-7777-8888', 'photo': 'https://i.pinimg.com/736x/0f/6d/83/0f6d83a38e05b52edf9e63d18d0c53eb.jpg'}
        ]

        for cust in data_customers:
            cust_exist = User.query.filter_by(username=cust['username']).first()
            if not cust_exist:
                hashed_password = generate_password_hash('customer123')
                new_customer = User(
                    name=cust['name'], username=cust['username'], email=cust['email'],
                    password=hashed_password, phone=cust['phone'], photo=cust.get('photo'),
                    role='customer', is_active=True
                )
                db.session.add(new_customer)
        
        db.session.commit()
        print(f"✅ Berhasil: Data Akun Customer dipastikan tersedia!")
            
        # ==========================================
        # 7. SEEDER KATEGORI MENU
        # ==========================================
        daftar_kategori = [
            {'nama': 'Food', 'type': 'food'},
            {'nama': 'Snack', 'type': 'food'},
            {'nama': 'Coffee', 'type': 'beverage'},
            {'nama': 'Non Coffee', 'type': 'beverage'}
        ]
        
        for kat in daftar_kategori:
            kategori_exist = Category.query.filter_by(name=kat['nama']).first()
            if not kategori_exist:
                db.session.add(Category(name=kat['nama'], type=kat['type']))
                
        db.session.commit()

        # ==========================================
        # 8. SEEDER MENU
        # ==========================================
        kategori_db = {k.name: k.id for k in Category.query.all()}

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
                db.session.add(Menu(
                    name=item['nama'], category_id=kategori_db[item['kategori']], price=item['harga'],
                    description=item['deskripsi'], stock=item['stok'], image_url=item.get('image_url'), is_available=True
                ))
        db.session.commit()
        print("✅ Berhasil: Data Menu ditambahkan!")

        # ==========================================
        # 9. SEEDER MEJA (TABLE) 
        # ==========================================
        data_meja = [
            {"nomor": "01", "kapasitas": 4, "tersedia": False},
            {"nomor": "02", "kapasitas": 2, "tersedia": False},
            {"nomor": "03", "kapasitas": 4, "tersedia": True}, 
            {"nomor": "04", "kapasitas": 6, "tersedia": False},
            {"nomor": "05", "kapasitas": 2, "tersedia": True},  
            {"nomor": "06", "kapasitas": 10, "tersedia": True},  
            {"nomor": "07", "kapasitas": 5, "tersedia": True},
            {"nomor": "08", "kapasitas": 3, "tersedia": True}  
        ]
        
        meja_db = {}
        for meja in data_meja:
            m = Table.query.filter_by(table_number=meja["nomor"]).first()
            if not m:
                m = Table(table_number=meja["nomor"], capacity=meja["kapasitas"], is_available=meja["tersedia"])
                db.session.add(m)
                db.session.commit()
            meja_db[meja["nomor"]] = m.id

        # ==========================================
        # 10. SEEDER ORDER & ORDER ITEMS (SINKRONISASI KRONOLOGIS FIFO)
        # ==========================================
        customers_db = User.query.filter_by(role='customer').all()
        kasir_user = User.query.filter_by(role='kasir').first()
        kasir_id = kasir_user.id if kasir_user else None

        # Mengambil ID Koki untuk simulasi pengerjaan pesanan
        koki_user = User.query.filter_by(role='koki').first()
        koki_id = koki_user.id if koki_user else None
        
        menu_ayam = Menu.query.filter_by(name="Ayam Geprek").first()
        menu_kentang = Menu.query.filter_by(name="Kentang Goreng").first()
        menu_indomie = Menu.query.filter_by(name="Indomie Kuah").first()
        menu_avocado = Menu.query.filter_by(name="Avocado Juice").first()
        menu_dimsum = Menu.query.filter_by(name="Dimsum").first()
        menu_americano = Menu.query.filter_by(name="Americano").first()
        
        fallback_id = Menu.query.first().id if Menu.query.first() else 1
        now_utc = datetime.utcnow()

        data_orders = [
            # ── [URUTAN 1 - TERLAMA] 2 Jam Lalu: Sudah Selesai Disajikan Sepenuhnya
            {
                "order_number": "ORD-20260514-001",
                "user_id": customers_db[0].id if len(customers_db) > 0 else 1,
                "cashier_id": None,
                "customer_name": None,
                "table_id": meja_db.get("01"), 
                "table_number_snapshot": "01",
                "order_type": "dine_in",
                "order_status": "served",
                "payment_method": "qris",
                "payment_status": "paid",
                "total_amount": 50000,
                "created_at": now_utc - timedelta(hours=2),
                "items": [
                    {"menu_id": menu_ayam.id if menu_ayam else fallback_id, "qty": 1, "price": 20000, "notes": "Pedas manis", "status": "served", "koki_id": koki_id, "prepared_at": now_utc - timedelta(hours=2) + timedelta(minutes=2), "ready_at": now_utc - timedelta(hours=2) + timedelta(minutes=14)},
                    {"menu_id": menu_kentang.id if menu_kentang else fallback_id, "qty": 2, "price": 15000, "notes": "Saus pisah", "status": "served", "koki_id": koki_id, "prepared_at": now_utc - timedelta(hours=2) + timedelta(minutes=3), "ready_at": now_utc - timedelta(hours=2) + timedelta(minutes=10)}
                ]
            },
            # ── [URUTAN 2] 45 Menit Lalu: Makanan Matang Siap Saji di Meja Counter
            {
                "order_number": "ORD-20260514-002",
                "user_id": None,
                "cashier_id": kasir_id,
                "customer_name": "Tamu Meja 2",
                "table_id": meja_db.get("02"),
                "table_number_snapshot": "02",
                "order_type": "dine_in",
                "order_status": "ready",
                "payment_method": "qris",
                "payment_status": "paid",
                "total_amount": 29000,
                "created_at": now_utc - timedelta(minutes=45),
                "items": [
                    {"menu_id": menu_indomie.id if menu_indomie else fallback_id, "qty": 1, "price": 12000, "notes": "Kuah dikit", "status": "ready", "koki_id": koki_id, "prepared_at": now_utc - timedelta(minutes=43), "ready_at": now_utc - timedelta(minutes=35)},
                    {"menu_id": menu_avocado.id if menu_avocado else fallback_id, "qty": 1, "price": 17000, "notes": "No sugar", "status": "served", "koki_id": koki_id, "prepared_at": now_utc - timedelta(minutes=42), "ready_at": now_utc - timedelta(minutes=38)}
                ]
            },
            # ── [URUTAN 3] 30 Menit Lalu: Kasus Pembatalan Iseng Meja 8
            {
                "order_number": "ORD-20260514-010",
                "user_id": None,
                "cashier_id": kasir_id,
                "customer_name": "Tamu Meja 8 Iseng",
                "table_id": None,
                "table_number_snapshot": "08",
                "order_type": "dine_in",
                "order_status": "pending",
                "payment_method": "cash",
                "payment_status": "cancelled",
                "cancellation_reason": "Pelanggan salah pencet menu dan buru-buru pergi karena ada urusan mendadak.",
                "total_amount": 15000,
                "created_at": now_utc - timedelta(minutes=30),
                "items": [
                    {"menu_id": menu_americano.id if menu_americano else fallback_id, "qty": 1, "price": 15000, "notes": "No sugar", "status": "pending"}
                ]
            },
            # ── [URUTAN 4] 15 Menit Lalu: Mandiri App (Lunas Paid) - Sedang Dimasak Campuran
            {
                "order_number": "ORD-20260514-008",
                "user_id": customers_db[1].id if len(customers_db) > 1 else 2,
                "cashier_id": None,
                "customer_name": None,
                "table_id": meja_db.get("01"),
                "table_number_snapshot": "01",
                "order_type": "dine_in",
                "order_status": "preparing",
                "payment_method": "qris",
                "payment_status": "paid",
                "total_amount": 32000,
                "created_at": now_utc - timedelta(minutes=15),
                "items": [
                    {"menu_id": menu_indomie.id if menu_indomie else fallback_id, "qty": 1, "price": 12000, "notes": "Pakai cabe potong", "status": "preparing", "koki_id": koki_id, "prepared_at": now_utc - timedelta(minutes=13)},
                    {"menu_id": menu_ayam.id if menu_ayam else fallback_id, "qty": 1, "price": 20000, "notes": "Sambal dipisah", "status": "pending"}
                ]
            },
            # ── [URUTAN 5] 7 Menit Lalu: Kasir Manual (Dine In + Unpaid) - Antrean Baru Pending
            {
                "order_number": "ORD-20260514-003",
                "user_id": None, 
                "cashier_id": kasir_id,
                "customer_name": "Pelanggan Meja 4",
                "table_id": meja_db.get("04"),
                "table_number_snapshot": "04",
                "order_type": "dine_in",
                "order_status": "pending", 
                "payment_method": "cash",
                "payment_status": "unpaid",
                "total_amount": 45000,
                "created_at": now_utc - timedelta(minutes=7),
                "items": [
                    {"menu_id": menu_dimsum.id if menu_dimsum else fallback_id, "qty": 3, "price": 15000, "notes": "Saus banyak", "status": "pending"}
                ]
            },
            # ── [URUTAN 6] 4 Menit Lalu: Kasir Manual - Take Away - Unpaid - Antrean Baru Pending
            {
                "order_number": "ORD-20260514-004",
                "user_id": None,
                "cashier_id": kasir_id,
                "customer_name": "Ojol Grab (Pak Joko)",
                "table_id": None,
                "table_number_snapshot": None,
                "order_type": "take_away",
                "order_status": "pending",
                "payment_method": "cash",
                "payment_status": "unpaid",
                "total_amount": 30000,
                "created_at": now_utc - timedelta(minutes=4),
                "items": [
                    {"menu_id": menu_americano.id if menu_americano else fallback_id, "qty": 1, "price": 15000, "notes": "Less ice", "status": "pending"},
                    {"menu_id": menu_kentang.id if menu_kentang else fallback_id, "qty": 1, "price": 15000, "notes": "Garam dikit", "status": "pending"}
                ]
            },
            # ── [URUTAN 7 - TERBARU] 2 Menit Lalu: Kasir Manual - Take Away - Lunas Paid - Antrean Baru Pending
            {
                "order_number": "ORD-20260514-009",
                "user_id": None,
                "cashier_id": kasir_id,
                "customer_name": "Mbak Rini (Walk-in TA)",
                "table_id": None,
                "table_number_snapshot": None,
                "order_type": "take_away",
                "order_status": "pending",
                "payment_method": "cash",
                "payment_status": "paid",
                "total_amount": 17000,
                "created_at": now_utc - timedelta(minutes=2),
                "items": [
                    {"menu_id": menu_avocado.id if menu_avocado else fallback_id, "qty": 1, "price": 17000, "notes": "Ekstra susu cokelat", "status": "pending"}
                ]
            },
            # ── PESANAN HISTORI HARI-HARI SEBELUMNYA (TABLE_ID WAJIB NULL AGAR TIDAK MENGUNCI MEJA AKTIF KASIR) ──
            {
                "order_number": "ORD-20260513-005",
                "user_id": customers_db[1].id if len(customers_db) > 1 else 1,
                "cashier_id": None, "customer_name": None, "table_id": None, 
                "table_number_snapshot": "03", "order_type": "dine_in", "order_status": "served",
                "payment_method": "qris", "payment_status": "paid", "total_amount": 20000,
                "created_at": now_utc - timedelta(days=1),
                "items": [
                    {"menu_id": menu_ayam.id if menu_ayam else fallback_id, "qty": 1, "price": 20000, "notes": "Sambal dipisah", "status": "served", "koki_id": koki_id, "prepared_at": now_utc - timedelta(days=1) + timedelta(minutes=2), "ready_at": now_utc - timedelta(days=1) + timedelta(minutes=15)}
                ]
            },
            {
                "order_number": "ORD-20260512-006",
                "user_id": customers_db[2].id if len(customers_db) > 2 else 1,
                "cashier_id": None, "customer_name": None, "table_id": None, 
                "table_number_snapshot": "05", "order_type": "dine_in", "order_status": "served",
                "payment_method": "cash", "payment_status": "paid", "total_amount": 40000,
                "created_at": now_utc - timedelta(days=2),
                "items": [
                    {"menu_id": menu_ayam.id if menu_ayam else fallback_id, "qty": 2, "price": 20000, "notes": "Satu pedas, satu sedang", "status": "served", "koki_id": koki_id, "prepared_at": now_utc - timedelta(days=2) + timedelta(minutes=3), "ready_at": now_utc - timedelta(days=2) + timedelta(minutes=18)}
                ]
            },
            {
                "order_number": "ORD-20260511-007",
                "user_id": customers_db[3].id if len(customers_db) > 3 else 1,
                "cashier_id": None, "customer_name": None, "table_id": None, 
                "table_number_snapshot": "01", "order_type": "dine_in", "order_status": "served",
                "payment_method": "qris", "payment_status": "paid", "total_amount": 20000,
                "created_at": now_utc - timedelta(days=3),
                "items": [
                    {"menu_id": menu_ayam.id if menu_ayam else fallback_id, "qty": 1, "price": 20000, "notes": "Dada mentok", "status": "served", "koki_id": koki_id, "prepared_at": now_utc - timedelta(days=3) + timedelta(minutes=1), "ready_at": now_utc - timedelta(days=3) + timedelta(minutes=12)}
                ]
            }
        ]

        for data in data_orders:
            order_exist = Order.query.filter_by(order_number=data["order_number"]).first()
            if not order_exist:
                pesanan_baru = Order(
                    order_number=data["order_number"], user_id=data["user_id"], cashier_id=data["cashier_id"],
                    customer_name=data["customer_name"], table_id=data["table_id"], table_number_snapshot=data.get("table_number_snapshot"),
                    order_type=data["order_type"], order_status=data["order_status"], payment_method=data["payment_method"],
                    payment_status=data["payment_status"], total_amount=data["total_amount"], cancellation_reason=data.get("cancellation_reason"),
                    created_at=data["created_at"]
                )
                db.session.add(pesanan_baru)
                db.session.commit()
                
                for item in data["items"]:
                    item_baru = OrderItem(
                        order_id=pesanan_baru.id, menu_id=item["menu_id"], qty=item["qty"],
                        price_at_order=item["price"], notes=item["notes"], item_status=item["status"],
                        koki_id=item.get("koki_id"), prepared_at=item.get("prepared_at"), ready_at=item.get("ready_at")
                    )
                    db.session.add(item_baru)
                db.session.commit()
        print("✅ Berhasil: Data Order & Detail Item dengan metrik Koki ditambahkan!")

        # ==========================================
        # 11. SEEDER RESERVASI
        # ==========================================
        customer = customers_db[0] if customers_db else None
        customer_id = customer.id if customer else 1
        customer_phone = customer.phone if customer and customer.phone else "081299998888"

        meja_db_id = {m.table_number: m.id for m in Table.query.all()}
        fallback_table = list(meja_db_id.values())[0] if meja_db_id else 1

        today_date = date.today()
        tomorrow_date = today_date + timedelta(days=1)
        yesterday_date = today_date - timedelta(days=1)

        data_reservasi = [
            {
                "user_id": customer_id, "reservation_number": f"RES-{today_date.strftime('%Y%m%d')}-001", 
                "customer_name": None, "phone": customer_phone, "guest_qty": 2, "duration": 90,
                "tables": [meja_db_id.get("02", fallback_table)], "notes": None, "cancellation_reason": None,
                "reservation_date": tomorrow_date, "reservation_time": time(19, 0), "status": "pending"
            },
            {
                "user_id": customer_id, "reservation_number": f"RES-{today_date.strftime('%Y%m%d')}-002",
                "customer_name": None, "phone": customer_phone, "guest_qty": 4, "duration": 120,
                "tables": [meja_db_id.get("01", fallback_table)], "notes": "Tolong siapkan kursi tinggi untuk balita.",
                "cancellation_reason": None, "reservation_date": today_date, "reservation_time": time(20, 0), "status": "confirmed"
            },
            {
                "user_id": None, "reservation_number": f"RES-{yesterday_date.strftime('%Y%m%d')}-001",
                "customer_name": "Ibu Ratna", "phone": "081999888777", "guest_qty": 8, "duration": 150,
                "tables": [meja_db_id.get("03", fallback_table), meja_db_id.get("04", fallback_table)], "notes": "Acara keluarga",
                "cancellation_reason": None, "reservation_date": yesterday_date, "reservation_time": time(12, 30), "status": "completed"
            }
        ]

        for data in data_reservasi:
            reservasi_exist = Reservation.query.filter_by(reservation_number=data["reservation_number"]).first()
            if not reservasi_exist:
                reservasi_baru = Reservation(
                    user_id=data["user_id"], reservation_number=data["reservation_number"],
                    customer_name=data["customer_name"], phone=data["phone"], guest_qty=data["guest_qty"],
                    duration=data["duration"], notes=data["notes"], cancellation_reason=data["cancellation_reason"],
                    reservation_date=data["reservation_date"], reservation_time=data["reservation_time"], status=data["status"]
                )
                db.session.add(reservasi_baru)
                db.session.commit()
                
                for t_id in data["tables"]:
                    table_obj = Table.query.get(t_id)
                    snapshot = table_obj.table_number if table_obj else "Unknown"
                    db.session.add(ReservationTable(reservation_id=reservasi_baru.id, table_id=t_id, table_number_snapshot=snapshot))
                db.session.commit()
        print("✅ Berhasil: Data Reservasi & Relasi Meja ditambahkan!")

        # ==========================================
        # 12. SEEDER REVIEW (AYAM GEPREK)
        # ==========================================
        if menu_ayam:
            ayam_items = OrderItem.query.filter_by(menu_id=menu_ayam.id, item_status='served').limit(4).all()
            reviews_data = [
                {"rating": 5, "comment": "Ayamnya sangat krispi dan sambalnya mantap luar biasa!"},
                {"rating": 4, "comment": "Porsinya cukup besar, rasanya enak tapi kurang pedas buat saya."},
                {"rating": 5, "comment": "Bumbu meresap sampai ke dalam, dagingnya empuk banget. Recommended!"},
                {"rating": 4, "comment": "Enak, harganya juga terjangkau. Pelayanan sangat cepat."}
            ]
            for i, item in enumerate(ayam_items):
                if i < len(reviews_data):
                    review_exist = Review.query.filter_by(order_item_id=item.id).first()
                    if not review_exist:
                        db.session.add(Review(order_item_id=item.id, rating=reviews_data[i]["rating"], comment=reviews_data[i]["comment"]))
            db.session.commit()
            print("✅ Berhasil: 4 Data Review untuk Ayam Geprek ditambahkan!")
        else:
            print("ℹ️ Lewati: Menu Ayam Geprek tidak ditemukan untuk diberikan ulasan.")
            
        print("--- SEEDER SELESAI ---\n")

if __name__ == '__main__':
    run_seeders()