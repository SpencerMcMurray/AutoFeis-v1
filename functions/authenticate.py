import gc
import re
from functions.databaseOps import email_taken
from werkzeug.security import check_password_hash
from database import Database


def fetch_signup_errors(form):
    """(Form) -> list of str
    Returns all errors generated from the given signup form
    """
    errors = list()
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", form.email.data):
        errors.append("Email given is not valid")
    if len(form.f_name.data) <= 0 or len(form.l_name.data) <= 0:
        errors.append("Name field(s) left blank")
    if len(form.f_name.data) > 100 or len(form.l_name.data) > 100:
        errors.append("Name field(s) too long")
    if len(form.email.data) <= 0:
        errors.append("Email field left blank")
    if len(form.email.data) > 255:
        errors.append("Email field too long")
    if len(form.password.data) <= 0:
        errors.append("Email field left blank")
    if len(form.password.data) > 100:
        errors.append("Email field too long")
    if email_taken(form.email.data):
        errors.append("The email provided already belongs to a user")
    if form.password.data != form.confirm.data:
        errors.append("The passwords given dont match")
    if not password_is_good(form.password.data):
        errors.append("Your password should contain at least 6 characters and a symbol")
    return errors


def fetch_login_errors(form):
    """(Form) -> list of str
    Returns all errors generated from the given login form
    """
    errors = list()
    if not email_taken(form.email.data):
        errors.append("The email given isn't registered with us")
    if not validate(form.email.data, form.password.data):
        errors.append("The password given is incorrect")
    return errors


def validate(email, password):
    """Returns True iff password is valid for given email"""
    db = Database()
    q = "SELECT * FROM `users` WHERE `email` = %s"
    num_rows = db.cur.execute(q, email)
    if num_rows == 0:
        return False
    res = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return check_password_hash(res["password"], password)


def password_is_good(pw):
    """(str) -> bool
    Returns True iff pw has at least 6 characters and 1 symbol
    """
    symbols = {'@', '#', '$', '%', '^', '&', '*'}
    for char in pw:
        if char in symbols:
            return True
    return False
