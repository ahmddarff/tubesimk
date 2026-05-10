# Tempat setup db = SQLAlchemy() agar tidak circular import

# pip install flask_sqlalchemy di terminal dulu sebelum pakai ini
from flask_sqlalchemy import SQLAlchemy

# Inisialisasi tanpa mengikat ke app dulu
db = SQLAlchemy()