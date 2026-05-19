from datetime import datetime
from models import Order, Reservation
from zoneinfo import ZoneInfo # Jika Python < 3.9, gunakan: from datetime import timezone, timedelta

def to_wib(dt_utc):
    """
    Mengonversi objek datetime UTC (baik naive maupun aware) dari database
    menjadi objek datetime aware dengan zona waktu Asia/Jakarta (WIB).
    Output: datetime.datetime(2026, 5, 19, 21, 25, tzinfo=ZoneInfo(key='Asia/Jakarta'))
    """
    if not dt_utc:
        return None
        
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))
        
    return dt_utc.astimezone(ZoneInfo("Asia/Jakarta"))

def format_tanggal_mentah(dt_utc):
    """
    Mengonversi datetime UTC dari DB ke Asia/Jakarta (WIB)
    dan mengembalikan string format kaku YYYY-MM-DD khusus untuk mesin filter kalender HTML.
    Output: string '2026-05-19'
    """
    if not dt_utc:
        return ""
    
    # Panggil fungsi to_wib yang ada di atasnya
    dt_wib = to_wib(dt_utc)
    
    return dt_wib.strftime('%Y-%m-%d') if dt_wib else ""

def format_tanggal_lokal(dt_utc):
    """
    Mengonversi datetime UTC dari DB ke Asia/Jakarta (WIB) 
    dan mengembalikan string format tanggal: 19 Mei 2026
    """
    # ✅ Panggil to_wib() sebagai pondasi utamanya
    dt_wib = to_wib(dt_utc)
    if not dt_wib:
        return ""
    
    # Format nama bulan Indonesia
    bulan_indo = [
        "Jan", "Feb", "Mar", "Apr", "Mei", "Juni",
        "Juli", "Ags", "Sep", "Okt", "Nov", "Des"
    ]
    
    day = dt_wib.day
    month = bulan_indo[dt_wib.month - 1]
    year = dt_wib.year
    
    return f"{day} {month} {year}"

def format_waktu_lokal(dt_utc):
    """
    Mengonversi datetime UTC dari DB ke Asia/Jakarta (WIB)
    dan mengembalikan string format waktu: 14:25 WIB
    """
    # ✅ Panggil to_wib() juga di sini!
    dt_wib = to_wib(dt_utc)
    if not dt_wib:
        return ""
        
    return dt_wib.strftime('%H:%M') + ' WIB'

def generate_order_number():
    """
    Menghasilkan nomor pesanan unik dengan format: ORD-YYYYMMDD-XXX
    Reset setiap hari.
    """
    # Ambil tanggal hari ini (contoh: 20260515)
    date_str = datetime.now().strftime('%Y%m%d')
    search_pattern = f"ORD-{date_str}-%"
    
    # Cari pesanan terakhir yang dibuat hari ini
    last_order = Order.query.filter(Order.order_number.like(search_pattern))\
                            .order_by(Order.id.desc()).first()
    
    if last_order:
        # Ambil bagian urutan terakhir (XXX), contoh: ORD-20260515-001 -> 001
        last_sequence = int(last_order.order_number.split('-')[-1])
        new_sequence = last_sequence + 1
    else:
        # Jika hari ini belum ada transaksi
        new_sequence = 1
        
    # Return dengan padding 3 digit (001, 002, dst)
    return f"ORD-{date_str}-{new_sequence:03d}"

def generate_reservation_number():
    """
    Menghasilkan nomor reservasi unik dengan format: RES-YYYYMMDD-XXX
    Reset setiap hari.
    """
    date_str = datetime.now().strftime('%Y%m%d')
    search_pattern = f"RES-{date_str}-%"
    
    last_res = Reservation.query.filter(Reservation.reservation_number.like(search_pattern))\
                                .order_by(Reservation.id.desc()).first()
    
    if last_res:
        last_sequence = int(last_res.reservation_number.split('-')[-1])
        new_sequence = last_sequence + 1
    else:
        new_sequence = 1
        
    return f"RES-{date_str}-{new_sequence:03d}"

def auto_sync_order_status(order):
    """
    Fungsi untuk menyinkronkan status Order Induk berdasarkan status anak-anaknya (OrderItems).
    Panggil fungsi ini SETELAH melakukan perubahan pada item_status, sebelum db.session.commit().
    """
    if not order.items:
        return
        
    # Kumpulkan semua status dari item anak
    statuses = [item.item_status for item in order.items]
    
    # Aturan 1: Jika SEMUA item sudah 'served' -> Order jadi 'served'
    if all(s == 'served' for s in statuses):
        order.order_status = 'served'
        
    # Aturan 2: Jika SEMUA item sudah matang ('ready' atau 'served') -> Order jadi 'ready'
    # Artinya tidak ada lagi yang 'pending' atau 'preparing'
    elif not any(s in ['pending', 'preparing'] for s in statuses):
        order.order_status = 'ready'
        
    # Aturan 3: Jika MINIMAL ADA 1 item yang sedang dimasak ('preparing', 'ready', atau 'served') 
    # dan masih ada yang 'pending' -> Order jadi 'preparing'
    elif any(s in ['preparing', 'ready', 'served'] for s in statuses):
        # Mencegah order turun status (misal dari ready kembali ke preparing)
        if order.order_status == 'pending':
            order.order_status = 'preparing'