from flask import Blueprint, render_template, request, redirect, url_for

# Inisialisasi Blueprint untuk Auth
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # TODO: Tambahkan validasi username dan password dari database
        # return redirect(url_for('kasir_dashboard')) atau return redirect('/customer')
        pass
    
    # Render template login dari root folder templates
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # TODO: Validasi dan Simpan ke Database
        # return redirect(url_for('auth.login')) dengan pesan sukses
        pass
        
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    # TODO: Hapus session user saat logout
    return redirect(url_for('auth.login'))