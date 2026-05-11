import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database, drop_database
from app import app, db
from seeders import run_seeders

load_dotenv()

def init_database():
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_DATABASE")
    
    ROOT_USER = os.getenv("DB_ROOT_USERNAME")
    ROOT_PASS = os.getenv("DB_ROOT_PASSWORD") or ""
    ROOT_URI = f'mysql+pymysql://{ROOT_USER}:{ROOT_PASS}@{DB_HOST}/{DB_NAME}'

    APP_USER = os.getenv("DB_APP_USERNAME")
    APP_PASS = os.getenv("DB_APP_PASSWORD")

    with app.app_context():
        # 1. RESET DATABASE (DROP & CREATE)
        if database_exists(ROOT_URI):
            print(f"Menghapus database lama '{DB_NAME}'...")
            drop_database(ROOT_URI)
        
        print(f"Menciptakan database baru '{DB_NAME}'...")
        create_database(ROOT_URI)
        # if not database_exists(ROOT_URI):
        #     create_database(ROOT_URI)
        #     print(f"Database '{DB_NAME}' berhasil dibuat!")
        # else:
        #     print(f"Database '{DB_NAME}' sudah ada.")
        
        # 2. Pembuatan Akun MySQL Otomatis
        root_engine = create_engine(ROOT_URI)
        with root_engine.connect() as conn:
            conn.execute(text(f"DROP USER IF EXISTS '{APP_USER}'@'localhost';"))
            conn.execute(text(f"CREATE USER '{APP_USER}'@'localhost' IDENTIFIED BY '{APP_PASS}';"))
            conn.execute(text(f"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{APP_USER}'@'localhost';"))
            conn.execute(text("FLUSH PRIVILEGES;"))
            print(f"Akun MySQL '{APP_USER}' berhasil disiapkan secara otomatis!")
        
        # 3. Pembuatan Tabel menggunakan APP_URI dari app.py
        db.create_all()
        print("Tabel-tabel berhasil di-generate/diperbarui!")

        # 4. DATA SEEDER (PENGHUNI AWAL DATABASE)
        run_seeders()

if __name__ == '__main__':
    print("Memulai proses setup database...")
    init_database()
    print("Setup selesai 100%. Kamu bisa mulai menjalankan app.py sekarang.")