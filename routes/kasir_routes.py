from flask import Blueprint, render_template

kasir_bp = Blueprint('kasir', __name__)

# =========================
# DASHBOARD
# =========================
@kasir_bp.route('/dashboard')
def dashboard():
    katalog_menu = [
        {"nama": "Terralog Kopi", "harga": 18000, "img": "kopi.png", "rating": 4.7, "terjual": 11, "status": "tersedia"},
        {"nama": "Espresso", "harga": 10000, "img": "kopi.png", "rating": 4.8, "terjual": 5, "status": "tersedia"},
        {"nama": "Sanger", "harga": 18000, "img": "kopi.png", "rating": 4.6, "terjual": 4, "status": "tersedia"},
        {"nama": "Americano", "harga": 15000, "img": "kopi.png", "rating": 4.3, "terjual": 8, "status": "tersedia"},
        {"nama": "Cappuccino", "harga": 18000, "img": "kopi.png", "rating": 4.5, "terjual": 5, "status": "tersedia"},
        {"nama": "Kopi Latte", "harga": 16000, "img": "kopi.png", "rating": 4.3, "terjual": 4, "status": "habis"},
        {"nama": "Americano", "harga": 15000, "img": "kopi.png", "rating": 4.3, "terjual": 8, "status": "tersedia"},
        {"nama": "Cappuccino", "harga": 18000, "img": "kopi.png", "rating": 4.5, "terjual": 5, "status": "tersedia"},
        {"nama": "Kopi Latte", "harga": 16000, "img": "kopi.png", "rating": 4.3, "terjual": 4, "status": "habis"},
    ]

    return render_template(
        'kasir/dashboard.html',
        menu=katalog_menu,
        segment='dashboard',
        role='kasir'
    )


# =========================
# PESANAN AKTIF
# =========================
@kasir_bp.route('/pesanan-aktif')
def pesanan_aktif():
    pesanan_list = [
        {"id": "P052", "nama": "Agnes", "meja": "07", "status": "PENDING", "total": 48000, "waktu": "12.12", "tipe": "DINE IN"},
        {"id": "P051", "nama": "Joy", "meja": "-", "status": "PENDING", "total": 48000, "waktu": "11.56", "tipe": "TAKE AWAY"},
        {"id": "P049", "nama": "Rahma", "meja": "06", "status": "READY", "total": 48000, "waktu": "11.27", "tipe": "DINE IN"},
        {"id": "P045", "nama": "Sonya", "meja": "03", "status": "SERVED", "total": 48000, "waktu": "10.40", "tipe": "DINE IN"},
    ]

    return render_template(
        'kasir/pesanan_aktif.html',
        segment='pesanan_aktif',
        role='kasir',
        pesanan=pesanan_list
    )


# =========================
# RESERVASI
# =========================
@kasir_bp.route('/reservasi')
def reservasi():
    data_reservasi = [
        {
            'id': '01',
            'nama': 'Richard Lim',
            'tanggal': '06/04/2024',
            'tamu': 2,
            'telepon': '0812345678',
            'waktu': '19.00',
            'status': 'Menunggu'
        },
    ]

    return render_template(
        'kasir/reservasi.html',
        segment='reservasi',
        role='kasir',
        reservations=data_reservasi
    )


# =========================
# RIWAYAT TRANSAKSI
# =========================
@kasir_bp.route('/riwayat-transaksi')
def riwayat_transaksi():
    stats_data = {
        'total_transaksi': 6,
        'total_penjualan': 450000,
        'tunai_persen': 50,
        'qris_persen': 50
    }

    transaksi_list = [
        {
            'id': 'TRX-00015',
            'tanggal': '2024-04-06',
            'waktu': '19.00',
            'pelanggan': 'Richard Lim',
            'kasir': 'Rahma',
            'metode': 'TUNAI',
            'total': 50000,
            'items': [
                {
                    'nama': 'Chicken Katsu',
                    'harga': 50000,
                    'jumlah': 1,
                    'subtotal': 50000
                }
            ]
        }
    ]

    return render_template(
        'kasir/riwayat_transaksi.html',
        segment='riwayat_transaksi',
        stats=stats_data,
        transactions=transaksi_list,
        role='kasir'
    )


# =========================
# PENGATURAN
# =========================
@kasir_bp.route('/pengaturan')
def pengaturan():
    return render_template(
        'kasir/pengaturan.html',
        segment='pengaturan',
        role='kasir'
    )