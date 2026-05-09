# Tempat menaruh semua Class tabel database

from sqlalchemy import CheckConstraint
from datetime import datetime

from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    username    = db.Column(db.String(50), unique=True, nullable=False)
    email       = db.Column(db.String(120), unique=True, nullable=True) # Tetap ada tapi nullable (opsional)
    password    = db.Column(db.String(255), nullable=False) # Simpan hasil hash, bukan plain text
    phone       = db.Column(db.String(20), nullable=True)
    role        = db.Column(db.Enum('owner', 'kasir', 'koki', 'customer', name='user_roles'), nullable=False)

    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi ke transaksi & reservasi
    orders      = db.relationship('Order', backref='user', lazy=True)
    reservations = db.relationship('Reservation', backref='user', lazy=True)

class CafeSetting(db.Model):
    __tablename__ = 'cafe_settings'
    id                      = db.Column(db.Integer, primary_key=True)
    is_open                 = db.Column(db.Boolean, default=True)
    open_time               = db.Column(db.Time, nullable=False)
    close_time              = db.Column(db.Time, nullable=False)
    reservation_buffer_time = db.Column(db.Integer, default=90) # Dalam menit
    table_clearance_time    = db.Column(db.Integer, default=15) # Dalam menit
    
    updated_at              = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Category(db.Model):
    __tablename__ = 'categories'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(50), nullable=False)

    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi 1 to Many ke Menus
    menus = db.relationship('Menu', backref='category', lazy=True)

class Menu(db.Model):
    __tablename__ = 'menus'
    id              = db.Column(db.Integer, primary_key=True)
    category_id     = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name            = db.Column(db.String(100), nullable=False)
    description     = db.Column(db.Text, nullable=True)
    price           = db.Column(db.Integer, nullable=False)
    image_url       = db.Column(db.String(255), nullable=True)
    is_available    = db.Column(db.Boolean, default=True)

    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi ke order_items
    order_items = db.relationship('OrderItem', backref='menu', lazy=True)

class Table(db.Model):
    __tablename__ = 'tables'
    id              = db.Column(db.Integer, primary_key=True)
    table_number    = db.Column(db.String(10), unique=True, nullable=False)
    capacity        = db.Column(db.Integer, nullable=False)
    is_available    = db.Column(db.Boolean, default=True) # Fisik meja: True=Kosong, False=Dipakai

    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi
    reservations = db.relationship('Reservation', backref='table', lazy=True)
    orders = db.relationship('Order', backref='table', lazy=True)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id                  = db.Column(db.Integer, primary_key=True)
    user_id             = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    customer_name       = db.Column(db.String(100), nullable=True)
    phone               = db.Column(db.String(20), nullable=True)
    table_id            = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=False)
    reservation_date    = db.Column(db.Date, nullable=False)
    reservation_time    = db.Column(db.Time, nullable=False)
    status              = db.Column(db.Enum('pending', 'confirmed', 'completed', 'cancelled', name='reservation_status'), default='pending')

    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at          = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Constraint untuk memastikan setidaknya user_id atau customer_name harus diisi
    __table_args__ = (
        CheckConstraint(
            'user_id IS NOT NULL OR customer_name IS NOT NULL', 
            name='check_reservation_user_or_name'
        ),
    )

class Order(db.Model):
    __tablename__ = 'orders'
    id              = db.Column(db.Integer, primary_key=True)
    order_number    = db.Column(db.String(50), unique=True, nullable=False)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    customer_name   = db.Column(db.String(100), nullable=True)
    table_id        = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=True) # Nullable untuk Take Away
    order_type      = db.Column(db.Enum('dine_in', 'take_away', name='order_type'), nullable=False)
    order_status    = db.Column(db.Enum('pending', 'preparing', 'ready', 'served', name='order_status'), default='pending')
    payment_method  = db.Column(db.Enum('cash', 'qris', name='payment_method'), nullable=True)
    payment_status  = db.Column(db.Enum('unpaid', 'paid', 'cancelled', name='payment_status'), default='unpaid')
    total_amount    = db.Column(db.Integer, nullable=False, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi ke item pesanan
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    # Constraint untuk memastikan setidaknya user_id atau customer_name harus diisi
    __table_args__ = (
        CheckConstraint(
            'user_id IS NOT NULL OR customer_name IS NOT NULL', 
            name='check_order_user_or_name'
        ),
    )

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id              = db.Column(db.Integer, primary_key=True)
    order_id        = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_id         = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)
    qty             = db.Column(db.Integer, nullable=False)
    price_at_order  = db.Column(db.Integer, nullable=False) # Snapshot harga dari menu
    notes           = db.Column(db.String(255), nullable=True)
    item_status     = db.Column(db.Enum('pending', 'preparing', 'ready', 'served', name='item_status'), default='pending')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi 1-to-1 ke Review (Mencegah review ganda)
    review = db.relationship('Review', backref='order_item', uselist=False, lazy=True)

class Review(db.Model):
    __tablename__ = 'reviews'
    id              = db.Column(db.Integer, primary_key=True)
    order_item_id   = db.Column(db.Integer, db.ForeignKey('order_items.id'), nullable=False, unique=True)
    rating          = db.Column(db.Integer, nullable=False)
    comment         = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)