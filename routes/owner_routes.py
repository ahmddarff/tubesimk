import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user 
from models import User, CafeSetting, OperationalHour, Menu, Category, Table, Order, OrderItem
from sqlalchemy import func
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

owner_bp = Blueprint('owner', __name__)

menu_data = [
    {"id": 1, "nama": "Espresso", "kategori": "Coffee", "harga": 20000},
    {"id": 2, "nama": "Matcha Latte", "kategori": "Non-Coffee", "harga": 25000},
    {"id": 3, "nama": "Croissant", "kategori": "Food", "harga": 18000}
]

staff_data = [
    {"id": 1, "nama": "Andi Pratama", "shift": "Pagi",  "status": "online",  "total_transaksi": 42},
    {"id": 2, "nama": "Budi Santoso", "shift": "Sore",  "status": "offline", "total_transaksi": 0},
]

kasir_data = [
    {"id": 1, "nama": "Dimas",   "total_transaksi": 7,  "total_penjualan": 350000, "status": "online"},
    {"id": 2, "nama": "Bg Ari",  "total_transaksi": 3,  "total_penjualan": 100000, "status": "offline"},
    {"id": 3, "nama": "Kak Aca", "total_transaksi": 15, "total_penjualan": 600000, "status": "online"}
]

@owner_bp.route('/dashboard')
@login_required
def dashboard():
    # 1. Hitung Stat Utama dari Database (Menggunakan total_amount sesuai models.py)
    total_penjualan_val = db.session.query(func.sum(Order.total_amount)).filter(Order.payment_status == 'paid').scalar() or 0
    total_order_val = Order.query.filter(Order.payment_status == 'paid').count()
    
    total_penjualan_formatted = f"Rp {total_penjualan_val:,}".replace(",", ".")

    # 2. Ambil Menu Terlaris dinamis dari OrderItem (Join Menu dan Order)
    menu_terlaris_query = db.session.query(Menu.name, func.sum(OrderItem.qty).label('total_qty'))\
        .join(OrderItem, OrderItem.menu_id == Menu.id)\
        .join(Order, OrderItem.order_id == Order.id)\
        .filter(Order.payment_status == 'paid')\
        .group_by(Menu.name)\
        .order_by(func.sum(OrderItem.qty).desc()).first()
        
    menu_terlaris_name = menu_terlaris_query[0] if menu_terlaris_query else "-"
    menu_terlaris_qty = menu_terlaris_query[1] if menu_terlaris_query else 0

    # 3. Data untuk Donut Chart (Kategori Terlaris - Join ke Category)
    category_data = db.session.query(Category.name, func.sum(OrderItem.qty))\
        .join(Menu, Menu.category_id == Category.id)\
        .join(OrderItem, OrderItem.menu_id == Menu.id)\
        .join(Order, OrderItem.order_id == Order.id)\
        .filter(Order.payment_status == 'paid')\
        .group_by(Category.name).all()
    
    chart_categories = [item[0] for item in category_data]
    chart_category_qtys = [int(item[1]) for item in category_data]

    # 4. Data untuk Line Chart (Pendapatan 7 Hari Terakhir)
    hari_ini = datetime.utcnow().date()
    tujuh_hari_lalu = hari_ini - timedelta(days=6)
    
    pendapatan_harian = db.session.query(
        func.date(Order.created_at).label('tanggal'),
        func.sum(Order.total_amount).label('total')
    ).filter(Order.payment_status == 'paid', Order.created_at >= tujuh_hari_lalu)\
     .group_by(func.date(Order.created_at))\
     .order_by(func.date(Order.created_at)).all()
     
    line_labels = [p.tanggal.strftime('%a') for p in pendapatan_harian] 
    line_values = [int(p.total) for p in pendapatan_harian]

    if not line_labels:
        line_labels = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
        line_values = [0, 0, 0, 0, 0, 0, 0]

    # 5. Data Staff Overview (Dinamis dari tabel User dan Order)
    # Melakukan outerjoin untuk menghitung berapa order yang ditangani setiap kasir/koki
    staff_query = db.session.query(
        User,
        func.count(Order.id).label('total_transaksi')
    ).outerjoin(Order, Order.cashier_id == User.id)\
     .filter(User.role.in_(['kasir', 'koki']))\
     .group_by(User.id).all()

    dinamis_staff_data = []
    for user, total_transaksi in staff_query:
        dinamis_staff_data.append({
            "nama": user.name,
            # Karena di database belum ada kolom 'shift', kita buat logika dummy sementara (Ganjil=Pagi, Genap=Sore)
            "shift": "Pagi" if user.id % 2 != 0 else "Sore",
            "status": "online" if user.is_active else "offline",
            "total_transaksi": total_transaksi
        })

    return render_template(
        'owner/dashboard.html',
        total_penjualan=total_penjualan_formatted,
        total_order=total_order_val,
        menu_terlaris=menu_terlaris_name,
        menu_terlaris_qty=menu_terlaris_qty,
        staff=dinamis_staff_data, 
        line_labels=line_labels,
        line_values=line_values,
        chart_categories=chart_categories,
        chart_category_qtys=chart_category_qtys
    )

@owner_bp.route('/manajemen-menu')
@login_required
def manajemen_menu():
    # Ambil semua data menu dan kategori dari database
    menus = Menu.query.all()
    categories = Category.query.all()
    return render_template('owner/manajemen-menu.html',
                           menu_list=menus, 
                           categories=categories)

@owner_bp.route('/manajemen-meja')
@login_required
def manajemen_meja():
    # Ambil semua data meja, urutkan berdasarkan nomor meja
    tables = Table.query.order_by(Table.table_number).all()
    return render_template('owner/manajemen-meja.html', tables=tables)

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
@owner_bp.route('/api/tambah-kategori', methods=['POST'])
@login_required
def tambah_kategori():
    nama = request.form.get('nama')
    if not nama:
        return jsonify({"success": False, "message": "Nama kategori tidak boleh kosong."})
    
    # Cek apakah nama kategori sudah ada agar tidak dobel
    exist = Category.query.filter_by(name=nama).first()
    if exist:
        return jsonify({"success": False, "message": "Kategori tersebut sudah ada."})
    
    new_cat = Category(name=nama)
    try:
        db.session.add(new_cat)
        db.session.commit()
        return jsonify({"success": True, "message": "Kategori baru berhasil ditambahkan!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@owner_bp.route('/api/edit-kategori/<int:id>', methods=['POST'])
@login_required
def edit_kategori(id):
    cat = db.session.get(Category, id)
    if not cat:
        return jsonify({"success": False, "message": "Kategori tidak ditemukan."})
    
    nama_baru = request.form.get('nama')
    if not nama_baru:
        return jsonify({"success": False, "message": "Nama kategori tidak boleh kosong."})
        
    # Cek duplikat dengan nama lain yang sudah ada
    exist = Category.query.filter(Category.name == nama_baru, Category.id != id).first()
    if exist:
        return jsonify({"success": False, "message": "Nama kategori ini sudah digunakan."})
        
    try:
        cat.name = nama_baru
        db.session.commit()
        return jsonify({"success": True, "message": "Nama kategori berhasil diubah!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@owner_bp.route('/api/hapus-kategori/<int:id>', methods=['POST'])
@login_required
def hapus_kategori(id):
    cat = db.session.get(Category, id)
    if not cat:
        return jsonify({"success": False, "message": "Kategori tidak ditemukan."})
        
    # VALIDASI PENTING: Cek apakah ada menu yang masih pakai kategori ini
    if cat.menus:
        return jsonify({
            "success": False, 
            "message": f"Gagal! Kategori ini sedang digunakan oleh {len(cat.menus)} menu. Pindahkan menu terlebih dahulu."
        })
        
    try:
        db.session.delete(cat)
        db.session.commit()
        return jsonify({"success": True, "message": "Kategori berhasil dihapus!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@owner_bp.route('/api/tambah-menu', methods=['POST'])
@login_required
def tambah_menu():
    try:
        # Mengambil data dari FormData
        nama = request.form.get('nama')
        kategori_nama = request.form.get('kategori') # Nama kategori dari dropdown
        harga = request.form.get('harga')
        stok_raw = request.form.get('stok')
        deskripsi = request.form.get('deskripsi')

        stok = int(stok_raw) if (stok_raw and stok_raw.strip() != "") else None
        
        # 1. Cari objek kategori berdasarkan nama untuk mendapatkan ID-nya
        category = Category.query.filter_by(name=kategori_nama).first()
        if not category:
            return jsonify({"success": False, "message": "Kategori tidak ditemukan."})

        # 2. Proses upload foto
        foto = request.files.get('foto')
        filename = None

        if foto and foto.filename != '':
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{foto.filename}")
            # Pastikan folder static/uploads/menu sudah dibuat
            upload_path = os.path.join(current_app.root_path, 'static/uploads/menu')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            
            foto.save(os.path.join(upload_path, filename))
            img_path = f"uploads/menu/{filename}"
        else:
            img_path = None # Atau path foto default

        # 3. Simpan ke Database menggunakan category_id (BUKAN category_name)
        new_menu = Menu(
            name=nama,
            category_id=category.id, # Menggunakan ID hasil pencarian di atas
            price=int(harga or 0),
            stock=stok,
            description=deskripsi,
            image_url=img_path,
            is_available=True
        )
        
        db.session.add(new_menu)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Menu berhasil ditambahkan!"})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

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

@owner_bp.route('/api/edit-menu/<int:menu_id>', methods=['POST'])
@login_required
def edit_menu(menu_id):
    try:
        # Menggunakan get yang aman untuk mengambil data menu
        menu = db.session.get(Menu, menu_id)
        if not menu:
            return jsonify({"success": False, "message": "Menu tidak ditemukan."})

        # Update data dasar
        menu.name = request.form.get('nama')
        menu.price = int(request.form.get('harga') or 0)
        menu.description = request.form.get('deskripsi')
        
        # Tangkap status ketersediaan (konversi string 'true'/'false' dari JS ke Boolean)
        status_str = request.form.get('status')
        menu.is_available = True if status_str == 'true' else False
        
        # Logika Manajemen Stok (NULL untuk menu yang dimasak/made-to-order)
        stok_raw = request.form.get('stok')
        menu.stock = int(stok_raw) if (stok_raw and stok_raw.strip() != "") else None

        # Update Kategori berdasarkan nama yang dipilih
        kategori_nama = request.form.get('kategori')
        category = Category.query.filter_by(name=kategori_nama).first()
        if category:
            menu.category_id = category.id

        # Update Foto jika ada file baru yang diunggah
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto and foto.filename != '':
                filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{foto.filename}")
                upload_path = os.path.join(current_app.root_path, 'static/uploads/menu')
                
                # Pastikan folder tujuan ada
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                
                foto.save(os.path.join(upload_path, filename))
                menu.image_url = f"uploads/menu/{filename}"

        db.session.commit()
        return jsonify({"success": True, "message": "Perubahan berhasil disimpan!"})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

# ── Meja APIS ─────────────────────────────────────────
@owner_bp.route('/api/tambah-meja', methods=['POST'])
@login_required
def tambah_meja():
    nomor = request.form.get('nomor')
    kapasitas = request.form.get('kapasitas')

    if not nomor or not kapasitas:
        return jsonify({"success": False, "message": "Nomor dan kapasitas wajib diisi!"})
    
    # Cek apakah nomor meja sudah ada
    if Table.query.filter_by(table_number=nomor).first():
        return jsonify({"success": False, "message": "Nomor meja ini sudah terdaftar."})

    try:
        new_table = Table(table_number=nomor, capacity=int(kapasitas), is_available=True)
        db.session.add(new_table)
        db.session.commit()
        return jsonify({"success": True, "message": "Meja berhasil ditambahkan!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@owner_bp.route('/api/edit-meja/<int:id>', methods=['POST'])
@login_required
def edit_meja(id):
    table = db.session.get(Table, id)
    if not table:
        return jsonify({"success": False, "message": "Meja tidak ditemukan."})

    nomor_baru = request.form.get('nomor')
    kapasitas_baru = request.form.get('kapasitas')
    
    # Cek duplikat jika nomor meja diganti
    if nomor_baru != table.table_number:
        if Table.query.filter_by(table_number=nomor_baru).first():
            return jsonify({"success": False, "message": "Nomor meja tersebut sudah digunakan."})

    try:
        table.table_number = nomor_baru
        table.capacity = int(kapasitas_baru)
        db.session.commit()
        return jsonify({"success": True, "message": "Data meja berhasil diperbarui!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@owner_bp.route('/api/hapus-meja/<int:id>', methods=['POST'])
@login_required
def hapus_meja(id):
    table = Table.query.get_or_404(id)
    
    try:
        db.session.delete(table)
        db.session.commit()
        return jsonify({"success": True, "message": f"Meja {table.table_number} berhasil dihapus!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Gagal menghapus meja."})

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
    # Mengambil data dari FormData (request.form) bukan request.json
    nama = request.form.get("nama")
    telp = request.form.get("telp")
    alamat = request.form.get("alamat")
    email = request.form.get("email")
    
    cafe_info = CafeSetting.query.first()
    
    if cafe_info:
        cafe_info.cafe_name = nama or cafe_info.cafe_name
        cafe_info.phone = telp or cafe_info.phone
        cafe_info.address = alamat or cafe_info.address
        cafe_info.email = email or cafe_info.email
        
        # Cek apakah ada file logo yang dikirim
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '':
                # Hapus logo lama
                if cafe_info.logo:
                    old_path = os.path.join(current_app.root_path, 'static/images', cafe_info.logo)
                    if os.path.exists(old_path) and os.path.isfile(old_path):
                        try: os.remove(old_path)
                        except: pass
                # Simpan logo baru
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file.save(os.path.join(current_app.root_path, 'static/images', unique_filename))
                cafe_info.logo = unique_filename

        try:
            db.session.commit()
            return jsonify({"success": True, "message": "Profil cafe beserta logo berhasil disimpan!"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": "Gagal menyimpan ke database."})
            
    return jsonify({"success": False, "message": "Data pengaturan cafe tidak ditemukan."})

@owner_bp.route('/api/update-akun', methods=['POST'])
@login_required
def update_akun():
    nama = request.form.get("nama")
    username = request.form.get("username")
    email = request.form.get("email")
    no_hp = request.form.get("no_hp")
    
    user = User.query.get(current_user.id)
    
    if user:
        user.name = nama or user.name
        user.username = username or user.username
        user.email = email or user.email
        user.phone = no_hp or user.phone
        
        # Konsisten menggunakan 'photo'
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                upload_path = os.path.join(current_app.root_path, 'static/uploads/profile')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

                # Hapus foto lama
                if user.photo:
                    old_path = os.path.join(current_app.root_path, 'static', user.photo)
                    if not os.path.exists(old_path) and not user.photo.startswith('uploads/'):
                        old_path = os.path.join(current_app.root_path, 'static/images', user.photo)
                        
                    if os.path.exists(old_path) and os.path.isfile(old_path):
                        try: os.remove(old_path)
                        except: pass
                
                filename = secure_filename(file.filename)
                unique_filename = f"{user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                
                file.save(os.path.join(upload_path, unique_filename))
                
                # Simpan beserta alamat path relatifnya ke database
                user.photo = f"uploads/profile/{unique_filename}"

        try:
            db.session.commit()
            return jsonify({"success": True, "message": "Akun dan foto profil berhasil diperbarui!"})
        except Exception as e:
            db.session.rollback()
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
    
@owner_bp.route('/api/toggle-cafe-status', methods=['POST'])
@login_required
def toggle_cafe_status():
    data = request.json
    status_baru = data.get("status") # Menangkap nilai True/False
    
    # Ambil data pengaturan cafe
    cafe = CafeSetting.query.first()
    
    if cafe:
        cafe.is_open = status_baru
        try:
            db.session.commit()
            return jsonify({"success": True, "message": "Status operasional cafe diperbarui!"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)})
            
    return jsonify({"success": False, "message": "Data cafe tidak ditemukan."})

@owner_bp.route('/api/toggle-jam-operasional', methods=['POST'])
@login_required
def toggle_jam_operasional():
    data = request.json
    hari = data.get("hari")
    status_buka = data.get("buka") # Menangkap nilai checkbox (True/False)
    
    # Cari jadwal berdasarkan nama hari di kolom day_of_week
    jadwal = OperationalHour.query.filter_by(day_of_week=hari).first()
    
    if jadwal:
        jadwal.is_open = status_buka # Pastikan kolomnya adalah is_open
        try:
            db.session.commit()
            return jsonify({"success": True, "message": "Status berhasil diperbarui"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)})
            
    return jsonify({"success": False, "message": "Data hari tidak ditemukan"})