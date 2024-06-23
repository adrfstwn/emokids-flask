from flask import render_template, flash, redirect, url_for, request, current_app
from apps import db
from apps.forms import LoginForm, RegistrationForm
from apps.models import User
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse, urljoin

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
