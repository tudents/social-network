from flask import Blueprint, request, render_template, redirect, url_for, flash
from .models import User
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def user():
    return render_template("user.html", user=current_user)


@views.route('/search')
@login_required
def search_user():
    username = request.args.get('username')
    if not username:
        flash('Введите имя пользователя для поиска.', category='error')
        return redirect(url_for('views.user'))

    user = User.query.filter_by(username=username).first()
    if user:
        return redirect(url_for('views.user_profile', user_id=user.id))
    else:
        flash('Пользователь не найден.', category='error')
        return redirect(url_for('views.user'))


# маршрут для отображения профиля
@views.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)
