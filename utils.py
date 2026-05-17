from datetime import datetime
from models import Order, Reservation

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