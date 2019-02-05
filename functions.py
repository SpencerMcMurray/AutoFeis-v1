from database import Database
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import gc
import datetime as dt
import csv
import os
import math
import random as rnd
import re


"""  DANCER CREATION  """


def set_defaults_for_dancer(dancer, form):
    """(dict of str:obj, Form) -> Form
    Sets all the defaults values from the dancer to the form, and returns resultant form
    """
    form.f_name.default = dancer['fName']
    form.l_name.default = dancer['lName']
    form.gender.default = dancer['gender']
    form.year.default = dancer['birthYear']
    form.school.default = dancer['school']
    form.level.default = dancer['level']
    form.show.default = dancer['show']
    form.process()
    return form


def fetch_dancer_errors(form):
    """(Form) -> list of str
    Returns a list of all errors that can be said about the given form
    """
    errors = list()
    if len(form.f_name.data) <= 0 or len(form.l_name.data) <= 0:
        errors.append("Name field(s) left blank")
    if len(form.f_name.data) > 100 or len(form.l_name.data) > 100:
        errors.append("Name field(s) too long")
    return errors


def update_dancer(dancer_id, f_name, l_name, school, birth_year, level, gender, show):
    db = Database()
    q = """UPDATE `dancer` SET `fName` = %s, `lName` = %s, `birthYear` = %s, `school` = %s, `level` = %s,
    `gender` = %s, `show` = %s WHERE `id` = %s"""
    db.cur.execute(q, (f_name, l_name,  birth_year, school, level, gender, show, dancer_id))
    db.con.close()
    gc.collect()


def create_dancer(user_id, f_name, l_name, school, birth_year, level, gender, show):
    db = Database()
    q = """INSERT INTO `dancer` (`user`, `fName`, `lName`, `birthYear`, `school`, `level`, `gender`, `show`) VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s)"""
    db.cur.execute(q, (user_id, f_name, l_name, birth_year, school, level, gender, show))
    db.con.close()
    gc.collect()


def age_dropdown(is_single):
    choices = list()
    offset = (1 if is_single is not None else 2)
    for i in range(3, 100, offset):
        choices.append(str(i))
    return choices


def school_dropdown():
    with open("static/csv/schools.csv", 'r') as my_file:
        reader = csv.reader(my_file, delimiter='\t')
        regions = list()
        for row in list(reader):
            regions.append((row[0], row[0]))
        return regions


def year_dropdown():
    curr_year = dt.datetime.now().year
    choices = list()
    for i in range(curr_year, curr_year-100-1, -1):
        choices.append((str(i), str(i)))
    return choices


def get_feiseanna_with_forg(forg_id):
    db = Database()
    db.cur.execute("SELECT * FROM `feiseanna` WHERE `forg` = %s ORDER BY `date` ASC", forg_id)
    res = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return res


def get_feis_with_id(feis_id):
    db = Database()
    db.cur.execute("SELECT * FROM `feiseanna` WHERE `id` = %s", feis_id)
    res = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return res


def get_dancers_with_user(user_id):
    db = Database()
    db.cur.execute("SELECT * FROM `dancer` WHERE `user` = %s", user_id)
    res = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return res


def get_id_from_email(email):
    db = Database()
    num_rows = db.cur.execute("SELECT `id` FROM `users` WHERE `email` = %s", email)
    if num_rows > 0:
        return db.cur.fetchone()['id']
    db.con.close()
    gc.collect()
    return -1


def get_name_from_email(email):
    """Gets the users name from their email"""
    db = Database()
    q = "SELECT `name` FROM `users` WHERE `email` = %s"
    num_rows = db.cur.execute(q, email)
    if num_rows == 0:
        return ""
    res = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return res['name']


"""  LOGIN/SIGN UP  """


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
        errors.append("Your password should contain at least 6 characters, and contain a symbol")
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


def email_taken(email):
    """Returns True iff the email given exists in the database"""
    db = Database()
    q = "SELECT `email` FROM `users` WHERE `email` = %s"
    num_rows = db.cur.execute(q, (email,))
    db.con.close()
    gc.collect()
    return num_rows != 0


def password_is_good(pw):
    """(str) -> bool
    Returns True iff pw has at least 6 characters and 1 symbol
    """
    symbols = {'@', '#', '$', '%', '^', '&', '*'}
    for char in pw:
        if char in symbols:
            return True
    return False


def sign_up(email, password, f_name, l_name):
    q = "INSERT INTO `users` (`email`, `password`, `name`) VALUES (%s, %s, %s)"
    db = Database()
    name = f_name + " " + l_name
    db.cur.execute(q, (email, generate_password_hash(password), name))
    db.con.close()
    gc.collect()


def feis_name_from_id(feis_id):
    db = Database()
    q = "SELECT `name` FROM `feiseanna` WHERE `id` = %s"
    db.cur.execute(q, feis_id)
    name = db.cur.fetchone()['name']
    db.con.close()
    gc.collect()
    return name


def get_user_from_id(usr_id):
    """(int) -> dict of str:obj
    Returns the user with the given id
    """
    db = Database()
    q = """SELECT * FROM `users` WHERE `id` = %s"""
    db.cur.execute(q, usr_id)
    user = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return user


def get_user_from_email(usr_email):
    """(str) -> dict of str:obj
    Returns the user with the given email
    """
    db = Database()
    q = """SELECT * FROM `users` WHERE `email` = %s"""
    db.cur.execute(q, usr_email)
    user = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return user


"""  RESULTS  """


def get_comps_by_level(feis_id):
    """(int) -> dict of str:list of dict of str:obj
    Given the feis id, returns all competitions divided by their competitions
    """
    db = Database()
    q = """SELECT * FROM `competition` WHERE `feis` = %s ORDER BY `level`, `dance`, `minAge`"""
    comps = list()
    levels = list()
    db.cur.execute(q, feis_id)
    all = db.cur.fetchall()
    prev_level = ""
    for one in all:
        curr_level = one['level']
        if curr_level != prev_level:
            levels.append(curr_level)
            comps.append(list())
            prev_level = curr_level
        comps[-1].append(one)
    return levels, comps
