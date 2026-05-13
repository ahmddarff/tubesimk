from flask import Blueprint, render_template

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/')
def beranda():
    return render_template('customer/beranda.html', segment='customer', role='customer')

@customer_bp.route('/daftar-menu')
def daftar_menu():
    # Katalog Menu dengan kategori
    katalog_menu = [
        # Coffee
        {"id": "terralog-kopi", "nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "rating": 4.7, "terjual": 11, "status": "tersedia", "kategori": "coffee", "deskripsi": "Kopi khas Terralog dengan perpaduan biji kopi pilihan yang diolah secara profesional menghasilkan rasa yang seimbang antara pahit dan sedkit asam. Disajikan dengan tekstur yang halus dan aroma kuat, cocok untuk menemani aktivitas harian Anda. Bisa dimikati dalam pilihan hot maupun ice sesuai selera.", "review_count": 3, "reviews": [{"nama": "zhanghao indosat", "date": "2026-04-06", "rating": 5, "text": "Mantap kopinya👍👍, sesuai sama selera saya... btw ada info loker gak ya? Saya butuh kerja..."}, {"nama": "jiwoo telkomsel", "date": "2026-03-21", "rating": 5, "text": "kopi terenak sejagat raya ini, bakalan beli tiap hari lah pokoknya"}]},
        {"id": "espresso", "nama": "Espresso", "harga": 10000, "img": "kopi.png", "rating": 4.8, "terjual": 5, "status": "tersedia", "kategori": "coffee", "deskripsi": "Kopi espresso murni dengan shot yang kuat dan intense. Dibuat dari biji kopi premium yang disangrai khusus untuk menghasilkan crema yang nikmat.", "review_count": 2, "reviews": []},
        {"id": "sanger", "nama": "Sanger", "harga": 18000, "img": "kopi.png", "rating": 4.6, "terjual": 4, "status": "tersedia", "kategori": "coffee", "deskripsi": "Minuman kopi signature dengan sentuhan karamel yang manis. Kombinasi sempurna antara kopi dan krema.", "review_count": 1, "reviews": []},
        {"id": "americano", "nama": "Americano", "harga": 15000, "img": "kopi.png", "rating": 4.3, "terjual": 8, "status": "tersedia", "kategori": "coffee", "deskripsi": "Kopi americano yang ringan dengan rasa yang balanced. Cocok untuk yang tidak terlalu menyukai kopi yang pekat.", "review_count": 0, "reviews": []},
        {"id": "cappuccino", "nama": "Cappuccino", "harga": 18000, "img": "kopi.png", "rating": 4.5, "terjual": 5, "status": "tersedia", "kategori": "coffee", "deskripsi": "Cappuccino klasik dengan kombinasi espresso, steamed milk, dan foam yang sempurna.", "review_count": 0, "reviews": []},
        {"id": "kopi-latte", "nama": "Kopi Latte", "harga": 16000, "img": "kopi.png", "rating": 4.3, "terjual": 4, "status": "habis", "kategori": "coffee", "deskripsi": "Latte yang creamy dengan kopi yang smooth. Disajikan dengan milk yang dipanaskan hingga menciptakan tekstur yang lembut.", "review_count": 0, "reviews": []},
        {"id": "butter-coffee", "nama": "Butter Coffee", "harga": 20000, "img": "kopi.png", "rating": 4.4, "terjual": 7, "status": "tersedia", "kategori": "coffee", "deskripsi": "Kopi dengan tambahan butter untuk memberikan rasa yang kaya dan creamy. Trend terbaru yang sedang viral.", "review_count": 0, "reviews": []},
        {"id": "tiramisu-coffee", "nama": "Tiramisu Coffee", "harga": 19000, "img": "kopi.png", "rating": 4.6, "terjual": 6, "status": "tersedia", "kategori": "coffee", "deskripsi": "Kopi dengan cita rasa tiramisu yang manis dan nikmat. Perpaduan sempurna antara kopi dan dessert.", "review_count": 0, "reviews": []},
        
        # Non Coffee
        {"id": "milk-tea", "nama": "Milk Tea", "harga": 16000, "img": "tea.png", "rating": 4.5, "terjual": 9, "status": "tersedia", "kategori": "noncoffee", "deskripsi": "Milk tea yang premium dengan daun teh pilihan. Dibuat dengan milk yang berkualitas untuk hasil yang smooth dan creamy.", "review_count": 0, "reviews": []},
        {"id": "iced-tea", "nama": "Iced Tea", "harga": 12000, "img": "tea.png", "rating": 4.4, "terjual": 8, "status": "tersedia", "kategori": "noncoffee", "deskripsi": "Teh dingin yang segar dengan rasa yang natural. Cocok sebagai minuman penyegarkan di siang hari.", "review_count": 0, "reviews": []},
        {"id": "chocolate-drink", "nama": "Chocolate Drink", "harga": 14000, "img": "drink.png", "rating": 4.6, "terjual": 10, "status": "tersedia", "kategori": "noncoffee", "deskripsi": "Minuman cokelat premium yang creamy dan nikmat. Dibuat dari cokelat berkualitas tinggi untuk rasa yang authentic.", "review_count": 0, "reviews": []},
        
        # Food
        {"id": "croissant", "nama": "Croissant", "harga": 22000, "img": "food.png", "rating": 4.7, "terjual": 15, "status": "tersedia", "kategori": "food", "deskripsi": "Croissant yang buttery dan crispy dengan tekstur yang sempurna. Dibuat fresh setiap hari menggunakan bahan berkualitas premium.", "review_count": 0, "reviews": []},
        {"id": "sandwich", "nama": "Sandwich", "harga": 25000, "img": "food.png", "rating": 4.5, "terjual": 12, "status": "tersedia", "kategori": "food", "deskripsi": "Sandwich dengan isian premium yang lezat dan filling. Cocok untuk sarapan atau makan siang ringan.", "review_count": 0, "reviews": []},
        {"id": "pasta", "nama": "Pasta", "harga": 35000, "img": "food.png", "rating": 4.6, "terjual": 8, "status": "tersedia", "kategori": "food", "deskripsi": "Pasta dengan sauce yang authentic dan bahan pilihan. Dibuat dengan resep traditional untuk cita rasa yang sesungguhnya.", "review_count": 0, "reviews": []},
        
        # Snack
        {"id": "cookies", "nama": "Cookies", "harga": 8000, "img": "snack.png", "rating": 4.4, "terjual": 20, "status": "tersedia", "kategori": "snack", "deskripsi": "Cookies yang renyah dengan rasa yang authentic. Cocok untuk dijadikan oleh-oleh atau cemilan santai.", "review_count": 0, "reviews": []},
        {"id": "donut", "nama": "Donut", "harga": 10000, "img": "snack.png", "rating": 4.5, "terjual": 18, "status": "tersedia", "kategori": "snack", "deskripsi": "Donut yang empuk dengan glazing yang nikmat. Tersedia dalam berbagai varian rasa yang menggugah selera.", "review_count": 0, "reviews": []},
        {"id": "muffin", "nama": "Muffin", "harga": 12000, "img": "snack.png", "rating": 4.3, "terjual": 14, "status": "tersedia", "kategori": "snack", "deskripsi": "Muffin yang lembut dengan rasa yang konsisten. Dibuat dari bahan premium untuk menghasilkan tekstur yang sempurna.", "review_count": 0, "reviews": []},
    ]
    return render_template('customer/daftar_menu.html', menu=katalog_menu, segment='daftar_menu', role='customer')

@customer_bp.route('/menu/<menu_id>')
def menu_detail(menu_id):
    # Katalog Menu dengan kategori (sama seperti di daftar_menu)
    katalog_menu = [
        # Coffee
        {"id": "terralog-kopi", "nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "rating": 4.7, "terjual": 11, "status": "tersedia", "kategori": "coffee", "deskripsi": "Kopi khas Terralog dengan perpaduan biji kopi pilihan yang diolah secara profesional menghasilkan rasa yang seimbang antara pahit dan sedkit asam. Disajikan dengan tekstur yang halus dan aroma kuat, cocok untuk menemani aktivitas harian Anda. Bisa dimikati dalam pilihan hot maupun ice sesuai selera.", "review_count": 3, "reviews": [{"nama": "zhanghao indosat", "date": "2026-04-06", "rating": 5, "text": "Mantap kopinya👍👍, sesuai sama selera saya... btw ada info loker gak ya? Saya butuh kerja..."}, {"nama": "jiwoo telkomsel", "date": "2026-03-21", "rating": 5, "text": "kopi terenak sejagat raya ini, bakalan beli tiap hari lah pokoknya"}]},
        {"id": "espresso", "nama": "Espresso", "harga": 10000, "img": "kopi.png", "rating": 4.8, "terjual": 5, "status": "tersedia", "kategori": "coffee", "deskripsi": "Kopi espresso murni dengan shot yang kuat dan intense. Dibuat dari biji kopi premium yang disangrai khusus untuk menghasilkan crema yang nikmat.", "review_count": 2, "reviews": []},
        {"id": "sanger", "nama": "Sanger", "harga": 18000, "img": "kopi.png", "rating": 4.6, "terjual": 4, "status": "tersedia", "kategori": "coffee", "deskripsi": "Minuman kopi signature dengan sentuhan karamel yang manis. Kombinasi sempurna antara kopi dan krema.", "review_count": 1, "reviews": []},
        {"id": "americano", "nama": "Americano", "harga": 15000, "img": "kopi.png", "rating": 4.3, "terjual": 8, "status": "tersedia", "kategori": "coffee", "deskripsi": "Kopi americano yang ringan dengan rasa yang balanced. Cocok untuk yang tidak terlalu menyukai kopi yang pekat.", "review_count": 0, "reviews": []},
        {"id": "cappuccino", "nama": "Cappuccino", "harga": 18000, "img": "kopi.png", "rating": 4.5, "terjual": 5, "status": "tersedia", "kategori": "coffee", "deskripsi": "Cappuccino klasik dengan kombinasi espresso, steamed milk, dan foam yang sempurna.", "review_count": 0, "reviews": []},
        {"id": "kopi-latte", "nama": "Kopi Latte", "harga": 16000, "img": "kopi.png", "rating": 4.3, "terjual": 4, "status": "habis", "kategori": "coffee", "deskripsi": "Latte yang creamy dengan kopi yang smooth. Disajikan dengan milk yang dipanaskan hingga menciptakan tekstur yang lembut.", "review_count": 0, "reviews": []},
        {"id": "butter-coffee", "nama": "Butter Coffee", "harga": 20000, "img": "kopi.png", "rating": 4.4, "terjual": 7, "status": "tersedia", "kategori": "coffee", "deskripsi": "Kopi dengan tambahan butter untuk memberikan rasa yang kaya dan creamy. Trend terbaru yang sedang viral.", "review_count": 0, "reviews": []},
        {"id": "tiramisu-coffee", "nama": "Tiramisu Coffee", "harga": 19000, "img": "kopi.png", "rating": 4.6, "terjual": 6, "status": "tersedia", "kategori": "coffee", "deskripsi": "Kopi dengan cita rasa tiramisu yang manis dan nikmat. Perpaduan sempurna antara kopi dan dessert.", "review_count": 0, "reviews": []},
        
        # Non Coffee
        {"id": "milk-tea", "nama": "Milk Tea", "harga": 16000, "img": "tea.png", "rating": 4.5, "terjual": 9, "status": "tersedia", "kategori": "noncoffee", "deskripsi": "Milk tea yang premium dengan daun teh pilihan. Dibuat dengan milk yang berkualitas untuk hasil yang smooth dan creamy.", "review_count": 0, "reviews": []},
        {"id": "iced-tea", "nama": "Iced Tea", "harga": 12000, "img": "tea.png", "rating": 4.4, "terjual": 8, "status": "tersedia", "kategori": "noncoffee", "deskripsi": "Teh dingin yang segar dengan rasa yang natural. Cocok sebagai minuman penyegarkan di siang hari.", "review_count": 0, "reviews": []},
        {"id": "chocolate-drink", "nama": "Chocolate Drink", "harga": 14000, "img": "drink.png", "rating": 4.6, "terjual": 10, "status": "tersedia", "kategori": "noncoffee", "deskripsi": "Minuman cokelat premium yang creamy dan nikmat. Dibuat dari cokelat berkualitas tinggi untuk rasa yang authentic.", "review_count": 0, "reviews": []},
        
        # Food
        {"id": "croissant", "nama": "Croissant", "harga": 22000, "img": "food.png", "rating": 4.7, "terjual": 15, "status": "tersedia", "kategori": "food", "deskripsi": "Croissant yang buttery dan crispy dengan tekstur yang sempurna. Dibuat fresh setiap hari menggunakan bahan berkualitas premium.", "review_count": 0, "reviews": []},
        {"id": "sandwich", "nama": "Sandwich", "harga": 25000, "img": "food.png", "rating": 4.5, "terjual": 12, "status": "tersedia", "kategori": "food", "deskripsi": "Sandwich dengan isian premium yang lezat dan filling. Cocok untuk sarapan atau makan siang ringan.", "review_count": 0, "reviews": []},
        {"id": "pasta", "nama": "Pasta", "harga": 35000, "img": "food.png", "rating": 4.6, "terjual": 8, "status": "tersedia", "kategori": "food", "deskripsi": "Pasta dengan sauce yang authentic dan bahan pilihan. Dibuat dengan resep traditional untuk cita rasa yang sesungguhnya.", "review_count": 0, "reviews": []},
        
        # Snack
        {"id": "cookies", "nama": "Cookies", "harga": 8000, "img": "snack.png", "rating": 4.4, "terjual": 20, "status": "tersedia", "kategori": "snack", "deskripsi": "Cookies yang renyah dengan rasa yang authentic. Cocok untuk dijadikan oleh-oleh atau cemilan santai.", "review_count": 0, "reviews": []},
        {"id": "donut", "nama": "Donut", "harga": 10000, "img": "snack.png", "rating": 4.5, "terjual": 18, "status": "tersedia", "kategori": "snack", "deskripsi": "Donut yang empuk dengan glazing yang nikmat. Tersedia dalam berbagai varian rasa yang menggugah selera.", "review_count": 0, "reviews": []},
        {"id": "muffin", "nama": "Muffin", "harga": 12000, "img": "snack.png", "rating": 4.3, "terjual": 14, "status": "tersedia", "kategori": "snack", "deskripsi": "Muffin yang lembut dengan rasa yang konsisten. Dibuat dari bahan premium untuk menghasilkan tekstur yang sempurna.", "review_count": 0, "reviews": []},
    ]
    
    # Cari menu berdasarkan ID
    menu = next((item for item in katalog_menu if item['id'] == menu_id), None)
    if menu is None:
        return "Menu tidak ditemukan", 404
    
    return render_template('customer/menu_detail.html', menu=menu, segment='daftar_menu', role='customer')

@customer_bp.route('/buat-reservasi')
def buat_reservasi():
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
    
    return render_template('customer/buat_reservasi.html', segment='buat_reservasi', role='customer', active_reservations=active_reservations, history_reservations=history_reservations)

@customer_bp.route('/pesanan-saya')
def pesanan_saya():
    active_orders = [{"id": "AB123", "status": "Hidangkan", "date": "06 April 2026", "time": "15:15 WIB", "products": [{"nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "qty": 2}], "total": 43000}]
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
    return render_template('customer/pesanan_saya.html', segment='pesanan_saya', role='customer', active_orders=active_orders, history_orders=history_orders)

@customer_bp.route('/checkout')
def checkout():
    return render_template('customer/checkout.html', segment='checkout', role='customer')

@customer_bp.route('/profil')
def profil():
    return render_template('customer/profil.html', segment='profil', role='customer')

@customer_bp.route('/pesanan/<order_id>')
def pesanan_detail(order_id):
    return render_template('customer/pesanan_aktif_detail.html', segment='pesanan_saya', role='customer', order_id=order_id)

@customer_bp.route('/reservasi/new')
def reservasi_new():
    return render_template('customer/buat_reservasi_new.html', segment='buat_reservasi', role='customer')

@customer_bp.route('/reservasi/<reservation_id>')
def reservasi_detail(reservation_id):
    return render_template('customer/reservasi_detail.html', segment='buat_reservasi', role='customer', reservation_id=reservation_id)

@customer_bp.route('/reservasi/history')
def reservasi_history():
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
    return render_template('customer/reservasi_history.html', segment='buat_reservasi', role='customer', history_reservations=history_reservations)