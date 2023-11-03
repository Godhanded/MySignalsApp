from MySignalsApp.errors.handlers import UtilError
from MySignalsApp.models.base import get_uuid
from MySignalsApp.models.signals import Signal
from MySignalsApp.models.placed_signals import PlacedSignals
from MySignalsApp.models.user_tokens import UserTokens
from datetime import datetime, timedelta
from flask import current_app, url_for, render_template
from MySignalsApp import db, mail
from flask_mail import Message
from threading import Thread


# db helpers
def query_one_filtered(table, **kwargs):
    return db.session.execute(db.select(table).filter_by(**kwargs)).scalar_one_or_none()


def query_all_filtered(table, **kwargs):
    return db.session.execute(db.select(table).filter_by(**kwargs)).scalars().all()


def query_one(table):
    return db.session.execute(db.select(table)).scalar_one_or_none()


def query_all(table):
    return db.session.execute(db.select(table)).scalars().all()


def query_paginated(table, page):
    return db.paginate(
        db.select(table).order_by(table.date_created.desc()),
        per_page=15,
        page=page,
        error_out=False,
    )


def query_paginate_filtered(table, page, **kwargs):
    return db.paginate(
        db.select(table).filter_by(**kwargs).order_by(table.date_created.desc()),
        per_page=15,
        page=page,
        error_out=False,
    )


# token helpers
def get_reset_token(user, expires=datetime.utcnow() + timedelta(hours=1)):
    token = get_uuid()
    token_data = UserTokens(user_id=user.id, token=token, expiration=expires)
    token_data.insert()
    return token


def verify_reset_token(user_table, token):
    try:
        token_data = query_one_filtered(UserTokens, token=str(token))
        if not token_data:
            return None

        if datetime.utcnow() <= token_data.expiration:
            user = query_one_filtered(user_table, id=token_data.user_id)
            token_data.delete()
            return user
        else:
            token_data.delete()
            return None
    except Exception:
        raise UtilError("Internal server error", 500, "It's not you it's us")


# Flask Mail helpers


def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(user, url_func):
    token = get_reset_token(user)
    msg = Message(
        "Secret Link Request", sender="noreply@demo.com", recipients=[user.email]
    )
    msg.html = render_template(
        "mail_template.html", token=url_for(url_func, token=token, _external=True)
    )
    Thread(
        target=send_async_mail, args=(current_app._get_current_object(), msg)
    ).start()
    # mail.send(msg)
    # print(url_for(url_func, token=token, _external=True))


# session helpers


def has_permission(session, permission):
    user = session.get("user")

    if not user:
        raise UtilError("Unauthorized", 401, "You are not logged in")

    if permission not in user.get("permission"):
        raise UtilError("Unauthorized", 401, "You are not authorized to access this")

    return user.get("id")


def is_active(table, user_id):
    try:
        user = query_one_filtered(table, id=user_id)

        if not user:
            raise UtilError("Resource not found", 404, "The User does not exist")

        is_active = user.is_active

        if not is_active:
            raise UtilError("Unauthorized", 401, "Your account is not active")
        return user

    except Exception:
        raise UtilError("Internal server error", 500, "It's not you it's us")


# rating helpers


def calculate_rating(provider_id):
    ratings = (
        db.session.execute(
            db.select(PlacedSignals.rating)
            .join(PlacedSignals.signal)
            .filter(Signal.provider == provider_id)
        )
        .scalars()
        .all()
    )
    rating_total = 0
    for rating in ratings:
        rating_total += rating
    return round(rating_total / (len(ratings) if ratings else 1), 2)
