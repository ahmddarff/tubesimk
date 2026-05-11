from werkzeug.security import generate_password_hash
from app import app, db
from models import User

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
        # 2. SEEDER LAINNYA BISA DITAMBAHKAN DI SINI
        # ==========================================
        # Contoh nanti: if not Table.query.first(): ... dst
        
        print("--- SEEDER SELESAI ---\n")

# Ini memungkinkan file dijalankan langsung via terminal
if __name__ == '__main__':
    run_seeders()