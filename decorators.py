import logging

from functools import wraps
from flask import session, request, redirect, url_for


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'lawyer' not in session:
            logging.debug(request.url)
            return redirect(url_for('lawyer_login'))
        return f(*args, **kwargs)
    return wrapper
