from flask import render_template, flash, redirect, url_for, request, current_app
from apps import db
from apps.forms import LoginForm, RegistrationForm
from apps.models import User
from apps.models import Siswa
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse, urljoin
from .decorators import admin_required

# Home route
@current_app.route('/')

@current_app.route('/index')
@login_required
def index():
    try:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return render_template('home/index.html', title='Home')
    except Exception as e:
        current_app.logger.error(f"Error in index route: {e}")
        return "Internal Server Error", 500

# Admin dashboard route
@current_app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    try:
        if current_user.role != 'admin':
            return redirect(url_for('index'))
        return render_template('home/index_admin.html', title='Admin Dashboard')
    except Exception as e:
        current_app.logger.error(f"Error in admin_dashboard route: {e}")
        return "Internal Server Error", 500


# Route to display the data siswa page
@current_app.route('/data_siswa')
@login_required
@admin_required
def data_siswa():
    try:
        # Fetch all siswa data from the database
        all_siswa = Siswa.query.all()
        return render_template('siswa/data_siswa.html', title='Data Siswa', all_siswa=all_siswa)
    except Exception as e:
        current_app.logger.error(f"Error in data_siswa route: {e}")
        return "Internal Server Error", 500

# Route to add data
@current_app.route('/add_data_siswa', methods=['GET', 'POST'])
@login_required
@admin_required
def add_data_siswa():
    if request.method == 'POST':
        try:
            # Logic to add new data
            id_siswa = request.form['id_siswa']
            name = request.form['name']
            birth_date = request.form['birth_date']
            kelas = request.form['kelas']
            new_siswa = Siswa(id_siswa=id_siswa, name=name, birth_date=birth_date, kelas=kelas)
            db.session.add(new_siswa)
            db.session.commit()
            flash('Data siswa added successfully!')
            return redirect(url_for('data_siswa'))
        except Exception as e:
            current_app.logger.error(f"Error in add_data_siswa route: {e}")
            return "Internal Server Error", 500
    return render_template('siswa/create_data_siswa.html', title='Tambah Data Siswa')

# Route to edit data
@current_app.route('/edit_data_siswa/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_data_siswa(id):
    siswa = Siswa.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # Logic to edit data
            siswa.id_siswa = request.form['id_siswa']
            siswa.name = request.form['name']
            siswa.birth_date = request.form['birth_date']
            siswa.kelas = request.form['kelas']
            db.session.commit()
            flash('Data siswa updated successfully!')
            return redirect(url_for('data_siswa'))
        except Exception as e:
            current_app.logger.error(f"Error in edit_data_siswa route: {e}")
            return "Internal Server Error", 500
    return render_template('siswa/edit_data_siswa.html', title='Edit Data Siswa', siswa=siswa)

@current_app.route('/delete_data_siswa/<int:id>', methods=['POST'])
@login_required
def delete_data_siswa(id):
    try:
        siswa = Siswa.query.get_or_404(id)
        db.session.delete(siswa)
        db.session.commit()
        flash('Data siswa berhasil dihapus!')
    except Exception as e:
        current_app.logger.error(f"Error deleting siswa: {e}")
        flash('Terjadi kesalahan saat menghapus data siswa.', 'error')
    return redirect(url_for('data_siswa'))

# Login route
@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.role == 'admin':
                next_page = url_for('admin_dashboard')
            else:
                next_page = url_for('index')
        return redirect(next_page)
    return render_template('accounts/login.html', title='Sign In', form=form)

# Logout route
@current_app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Registration route
@current_app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='orangtua')  # Default role is 'orangtua'
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('accounts/register.html', title='Register', form=form)

