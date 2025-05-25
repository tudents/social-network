from flask import Blueprint, request, render_template, redirect, url_for, flash
from .models import User
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def user():
    return render_template("user.html", user=current_user)