import os
from flask import Blueprint, render_template, url_for, request, flash, redirect, url_for, current_app
from .models import User, Message
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime



auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.password:
            if check_password_hash(user.password, password):
                flash('You have been logged in', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.user'))
            else:
                flash('Invalid password', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template('login.html', boolean=True)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        userName = request.form.get('userName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Почта минимум 5 символов', category='error')
        elif len(userName) < 2:
            flash('Имя пользователя минимум 3 символа', category='error')
        elif password1 != password2:
            flash('Пароли должны совпадать :Ъ', category='error')
        elif len(password1) < 7:
            flash('Пароль минимум 8 символов', category='error')
        else:
            new_user = User(email=email, username=userName, password=generate_password_hash(password1, method='pbkdf2:sha256', salt_length=8))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Аккаунт создан, вы молодец', category='success')
            return redirect(url_for('views.user'))

    return render_template('sign_up.html')