from datetime import datetime
from models import Order

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