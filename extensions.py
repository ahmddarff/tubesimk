# Tempat setup db = SQLAlchemy() agar tidak circular import

# pip install flask_sqlalchemy di terminal dulu sebelum pakai ini
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager

# Inisialisasi tanpa mengikat ke app dulu
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()