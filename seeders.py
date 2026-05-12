from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Category, Menu

def run_seeders():
    # Gunakan app_context agar SQLAlchemy tahu database mana yang dipakai
    with app.app_context():
        print("\n--- MENJALANKAN DATA SEEDER ---")
        
        # ==========================================
        # 1. SEEDER AKUN OWNER
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
        # 2. SEEDER KATEGORI MENU
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
        # 3. SEEDER MENU
        # ==========================================
        # Mengambil data kategori dari database untuk mendapatkan ID-nya
        kategori_db = {k.name: k.id for k in Category.query.all()}

        # Data menu awal yang akan di-seed
        data_menu = [
            {"nama": "Ayam Geprek", "kategori": "Food", "harga": 20000, "deskripsi": "Ayam geprek pedas dengan sambal bawang"},
            {"nama": "Indomie Kuah", "kategori": "Food", "harga": 12000, "deskripsi": "Indomie rebus dengan telur dan sayur"},
            {"nama": "Kentang Goreng", "kategori": "Snack", "harga": 15000, "deskripsi": "Kentang goreng renyah porsi besar"},
            {"nama": "Americano", "kategori": "Coffee", "harga": 15000, "deskripsi": "Kopi hitam espresso dengan air"},
            {"nama": "Avocado Juice", "kategori": "Non Coffee", "harga": 17000, "deskripsi": "Minuman jus alpukat dengan susu segar"},
            {"nama": "Dimsum", "kategori": "Snack", "harga": 15000, "deskripsi": "Dimsum ayam udang isi 4 pcs"}
        ]

        for item in data_menu:
            menu_exist = Menu.query.filter_by(name=item['nama']).first()
            if not menu_exist:
                menu_baru = Menu(
                    name=item['nama'],
                    category_id=kategori_db[item['kategori']], # Mengambil ID kategori berdasarkan namanya
                    price=item['harga'],
                    description=item['deskripsi'],
                    is_available=True
                )
                db.session.add(menu_baru)
        
        db.session.commit()
        print("✅ Berhasil: Data Menu ditambahkan!")
        
        print("--- SEEDER SELESAI ---\n")

# Ini memungkinkan file dijalankan langsung via terminal
if __name__ == '__main__':
    run_seeders()