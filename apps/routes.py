from flask import render_template, flash, redirect, url_for, request, current_app
from apps import db
from apps.forms import LoginForm, RegistrationForm, ProfileForm
from apps.models import User
from apps.models import Siswa
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse, urljoin
from .decorators import admin_required
from flask import abort
from flask import request

# Home route
@current_app.route('/')
    
#index orang tua
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
@current_app.route('/edit_data_siswa-<int:id>', methods=['GET', 'POST'])
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

@current_app.route('/delete_data_siswa-<int:id>', methods=['POST'])
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

#profile
@current_app.route('/profile-<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    
    # Verifikasi bahwa pengguna yang sedang masuk hanya dapat mengakses profil mereka sendiri
    if current_user.id != user_id:
        abort(403)  # Mengembalikan error 403 Forbidden jika mencoba mengakses profil orang lain

    form = ProfileForm(obj=user)  # Populate the form with user data

    if form.validate_on_submit():
        form.populate_obj(user)  # Update user object with form data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile', user_id=user.id))

    return render_template('accounts/profile.html', title='Profile', user=user, form=form)

# Login route
@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        # Retrieve user based on username or email
        user = User.query.filter((User.username == form.username_or_email.data) | (User.email == form.username_or_email.data)).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                if user.role == 'admin':
                    next_page = url_for('admin_dashboard')
                else:
                    next_page = url_for('index')
            return redirect(next_page)

        flash('Invalid username or password', 'danger')

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

@current_app.errorhandler(403)
def page_not_found(e):
    return render_template('home/page-403.html'), 404
@current_app.errorhandler(404)
def page_not_found(e):
    return render_template('home/page-404.html'), 404
@current_app.errorhandler(500)
def page_not_found(e):
    return render_template('home/page-500.html'), 500
