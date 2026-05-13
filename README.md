# ☕ Terralog Cafe - Point of Sale (POS) & Reservation System

Sistem kasir dan manajemen reservasi berbasis web untuk Terralog Cafe, dibangun menggunakan Flask dan MySQL dengan arsitektur modular.

## 🛠️ Prasyarat (Prerequisites)
Sebelum menjalankan aplikasi ini, pastikan komputer Anda sudah terinstal:
* **Python 3.x**
* **MySQL Server** (direkomendasikan menggunakan Laragon atau XAMPP)

## 🚀 Cara Instalasi & Menjalankan Aplikasi

Ikuti langkah-langkah di bawah ini untuk menjalankan proyek secara lokal:

### 1. Clone Repository & Masuk ke Folder
```bash
git clone https://github.com/ahmddarff/tubesimk.git
cd tubes-imk
```

### 2. Install Dependencies
```bash
pip install python-dotenv
pip install flask_sqlalchemy
pip install sqlalchemy-utils
pip install Flask-SQLAlchemy pymysql
pip install flask_login
```

### 3. Copy File Environment
```bash
cp .env.example .env
```

### 4. Konfigurasi File `.env`
Uncomment dan ubah sesuai database lokal:
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=terralog_db
DB_ROOT_USERNAME=root
DB_ROOT_PASSWORD=
```

#### **Credential Khusus Aplikasi**
Tambahkan variabel dibawah ini untuk koneksi database aplikasi:
```env
DB_APP_USERNAME=isi_username_app_anda
DB_APP_PASSWORD=isi_password_app_anda

SECRET_KEY=isi_dengan_kunci_rahasia_bebas
```

### 5. Setup Database Otomatis
Pastikan service MYSQL sudah berjalan di Laragon/XAMPP. Kemudian jalankan skrip setup berikut:
```bash
python setup_db.py
```

### 6. Jalankan Server Flask
Setelah database siap, jalankan aplikasi utama:
```bash
python app.py
```
Aplikasi dapat diakses melalui browser pada http://127.0.0.1:50001