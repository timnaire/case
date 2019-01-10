import logging

from functools import wraps
from flask import session, request, redirect, url_for

def login_required_client(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'client' not in session:
            logging.debug(request.url)
            return redirect(url_for('client_login'))
        return f(*args, **kwargs)
    return wrapper

def login_required_lawyer(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'lawyer' not in session:
            logging.debug(request.url)
            return redirect(url_for('lawyer_login'))
        return f(*args, **kwargs)
    return wrapper
