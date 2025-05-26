from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import User, Message
from datetime import datetime

messages = Blueprint('messages', __name__)


@messages.route('/messages/<int:receiver_id>', methods=['GET', 'POST'])
@login_required
def message(receiver_id):
    receiver = User.query.get_or_404(receiver_id)

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            new_message = Message(
                sender_id=current_user.id,
                receiver_id=receiver_id,
                content=content,
                timestamp=datetime.utcnow()
            )
            db.session.add(new_message)
            db.session.commit()
            flash('Сообщение отправлено!', category='success')
            return redirect(url_for('messages.message', receiver_id=receiver_id))
        else:
            flash('Сообщение не может быть пустым', category='error')

    # уже полученные сообщения
    messages_sent = Message.query.filter_by(sender_id=current_user.id, receiver_id=receiver_id)
    messages_received = Message.query.filter_by(sender_id=receiver_id, receiver_id=current_user.id)
    conversation = messages_sent.union(messages_received).order_by(Message.timestamp).all()

    return render_template('messages.html', receiver=receiver, conversation=conversation)
