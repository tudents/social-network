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
            if user and check_password_hash(user.password, password):
                if user.is_blocked:
                    flash('Ваш аккаунт заблокирован.')
                    logout_user()
                    return redirect(url_for('auth.login'))

                login_user(user, remember=True)
                flash('Вы вошли в аккаунт', category='success')
                return redirect(url_for('views.user'))
            else:
                flash('Неправильный пароль', category='error')
        else:
            flash('Такая почта не зарегистрирована или написана неправильно.', category='error')

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

# пользователь обновляет личную информацию
@auth.route('/change-info', methods=['GET', 'POST'])
@login_required
def change_info():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        birth_date = request.form.get('birth_date')
        profile_picture = request.files.get('profile_picture')

        user = User.query.get(current_user.id)

        # обновление полей только если они заполнены
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if birth_date:
            try:
                # преобразование строки в объект даты
                user.birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Неверный формат даты. Используй ГГГГ-ММ-ДД', category='error')
                return redirect(url_for('auth.change_info'))

        # обработка фото
        profile_picture = request.files.get('profile_picture')

        user = User.query.get(current_user.id)

        if profile_picture and profile_picture.filename != '':
            filename = secure_filename(profile_picture.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)
            profile_picture.save(file_path)

            user.profile_picture = f'uploads/{filename}'

        db.session.commit()
        flash('Информация обновлена!', category='success')
        return redirect(url_for('views.user'))

    return render_template('change-info.html')


# админка
@auth.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Вы не админ', category='error')
        return redirect(url_for('auth.logout'))
    users = User.query.all()
    return render_template('admin.html', users=users)


# изменение инфы о пользователе админом
@auth.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user_by_admin(user_id):
    if not current_user.is_admin:
        flash('Вы не админ', category='error')
        return redirect(url_for('auth.logout'))
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        db.session.commit()
        flash('Данные обновлены.')
        return redirect(url_for('auth.admin'))
    return render_template('edit_user_by_admin.html', user=user)


# блокировка пользователей
@auth.route('/admin/toggle_block/<int:user_id>')
@login_required
def toggle_block(user_id):
    if not current_user.is_admin:
        flash('Вы не админ', category='error')
    user = User.query.get_or_404(user_id)
    user.is_blocked = not user.is_blocked
    db.session.commit()
    flash('Статус блокировки изменен.')
    return redirect(url_for('auth.admin'))