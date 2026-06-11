import os
from dotenv import load_dotenv
from app import app, db
from seeders import run_seeders

load_dotenv()

def init_database():
    with app.app_context():
        print("Mereset tabel-tabel di database Cloud...")
        # 1. Hapus semua tabel jika sudah ada (mencegah error duplikasi)
        db.drop_all()
        
        # 2. Buat ulang semua tabel sesuai dengan models.py
        print("Menciptakan ulang tabel-tabel...")
        db.create_all()
        print("Tabel-tabel berhasil di-generate!")

        # 3. Jalankan Data Seeder
        run_seeders()

if __name__ == '__main__':
    print("Memulai proses setup database...")
    init_database()
    print("Setup selesai 100%. Kamu bisa mulai menjalankan app.py sekarang.")