from flask import Blueprint, render_template

kasir_bp = Blueprint('kasir', __name__)

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


@kasir_bp.route('/pesanan-aktif')
def pesanan_aktif():
    pesanan_list = [
        {"id": "P052", "nama": "Agnes", "meja": "07", "status": "PENDING", "total": 48000, "waktu": "12.12", "tipe": "DINE IN"},
        {"id": "P051", "nama": "Joy", "meja": "-", "status": "PENDING", "total": 48000, "waktu": "11.56", "tipe": "TAKE AWAY"},
        {"id": "P049", "nama": "Rahma", "meja": "06", "status": "READY", "total": 48000, "waktu": "11.27", "tipe": "DINE IN"},
        {"id": "P045", "nama": "Sonya", "meja": "03", "status": "SERVED", "total": 48000, "waktu": "10.40", "tipe": "DINE IN"},
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
        },
        {
            'id': 'TRX-00016',
            'tanggal': '2024-04-06',
            'waktu': '19.15',
            'pelanggan': 'Arialdi Manday',
            'kasir': 'Rahma',
            'metode': 'QRIS',
            'total': 75000,
            'items': [
                {
                    'nama': 'Terralog Coffee',
                    'harga': 25000,
                    'jumlah': 2,
                    'subtotal': 50000
                },
                {
                    'nama': 'French Fries',
                    'harga': 25000,
                    'jumlah': 1,
                    'subtotal': 25000
                }
            ]
        },
        {
            'id': 'TRX-00017',
            'tanggal': '2024-04-06',
            'waktu': '19.45',
            'pelanggan': 'Chaterine Jelek',
            'kasir': 'Rahma',
            'metode': 'TUNAI',
            'total': 35000,
            'items': [
                {
                    'nama': 'Matcha Latte',
                    'harga': 35000,
                    'jumlah': 1,
                    'subtotal': 35000
                }
            ]
        },
        {
            'id': 'TRX-00018',
            'tanggal': '2024-04-07',
            'waktu': '10.00',
            'pelanggan': 'Aldrik Running',
            'kasir': 'Dimas',
            'metode': 'QRIS',
            'total': 120000,
            'items': [
                {
                    'nama': 'Beef Burger',
                    'harga': 45000,
                    'jumlah': 2,
                    'subtotal': 90000
                },
                {
                    'nama': 'Lemon Tea',
                    'harga': 15000,
                    'jumlah': 2,
                    'subtotal': 30000
                }
            ]
        },
        {
            'id': 'TRX-00019',
            'tanggal': '2024-04-07',
            'waktu': '11.30',
            'pelanggan': 'Rahmaini Erna',
            'kasir': 'Dimas',
            'metode': 'TUNAI',
            'total': 25000,
            'items': [
                {
                    'nama': 'Americano',
                    'harga': 25000,
                    'jumlah': 1,
                    'subtotal': 25000
                }
            ]
        },
        {
            'id': 'TRX-00020',
            'tanggal': '2024-04-07',
            'waktu': '13.10',
            'pelanggan': 'Earlin Pinky',
            'kasir': 'Dimas',
            'metode': 'QRIS',
            'total': 85000,
            'items': [
                {
                    'nama': 'Nasi Goreng Terralog',
                    'harga': 40000,
                    'jumlah': 1,
                    'subtotal': 40000
                },
                {
                    'nama': 'Caramel Macchiato',
                    'harga': 45000,
                    'jumlah': 1,
                    'subtotal': 45000
                }
            ]
        },
        {
            'id': 'TRX-00021',
            'tanggal': '2024-04-08',
            'waktu': '15.20',
            'pelanggan': 'Budi Santoso',
            'kasir': 'Rahma',
            'metode': 'TUNAI',
            'total': 60000,
            'items': [
                {
                    'nama': 'Spaghetti Carbonara',
                    'harga': 60000,
                    'jumlah': 1,
                    'subtotal': 60000
                }
            ]
        },
        {
            'id': 'TRX-00022',
            'tanggal': '2024-04-08',
            'waktu': '16.00',
            'pelanggan': 'Siti Aminah',
            'kasir': 'Rahma',
            'metode': 'QRIS',
            'total': 40000,
            'items': [
                {
                    'nama': 'Croissant Almond',
                    'harga': 40000,
                    'jumlah': 1,
                    'subtotal': 40000
                }
            ]
        },
        {
            'id': 'TRX-00023',
            'tanggal': '2024-04-08',
            'waktu': '18.45',
            'pelanggan': 'Andi Wijaya',
            'kasir': 'Rahma',
            'metode': 'TUNAI',
            'total': 110000,
            'items': [
                {
                    'nama': 'Double Espresso',
                    'harga': 30000,
                    'jumlah': 2,
                    'subtotal': 60000
                },
                {
                    'nama': 'Club Sandwich',
                    'harga': 50000,
                    'jumlah': 1,
                    'subtotal': 50000
                }
            ]
        },
        {
            'id': 'TRX-00024',
            'tanggal': '2024-04-09',
            'waktu': '09.15',
            'pelanggan': 'Dewi Lestari',
            'kasir': 'Dimas',
            'metode': 'QRIS',
            'total': 55000,
            'items': [
                {
                    'nama': 'Caffé Latte',
                    'harga': 35000,
                    'jumlah': 1,
                    'subtotal': 35000
                },
                {
                    'nama': 'Donut Glaze',
                    'harga': 20000,
                    'jumlah': 1,
                    'subtotal': 20000
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