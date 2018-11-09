from database import Database
from werkzeug.security import generate_password_hash, check_password_hash
import gc
import datetime as dt


def get_dancer_from_id(dancer_id):
    db = Database()
    q = "SELECT * FROM `dancers` WHERE `id` = %s"
    db.cur.execute(q, dancer_id)
    dancer = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return dancer


def delete_dancer_from_id(id):
    db = Database()
    q = "DELETE FROM `dancers` WHERE `id` = %s"
    db.cur.execute(q, (id,))
    db.con.close()
    gc.collect()


def alter_dancer(dancer_id, f_name, l_name, school, birth_year, level, gender, show):
    db = Database()
    q = """UPDATE `dancers` SET `fName` = %s, `lName` = %s, `birthYear` = %s, `school` = %s, `level` = %s,
    `gender` = %s, `show` = %s WHERE `id` = %s"""
    db.cur.execute(q, (f_name, l_name,  birth_year, school, level, gender, show, dancer_id))
    db.con.close()
    gc.collect()


def create_dancer(user_id, f_name, l_name, school, birth_year, level, gender, show):
    db = Database()
    q = """INSERT INTO `dancers` (`user`, `fName`, `lName`, `birthYear`, `school`, `level`, `gender`, `show`) VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s)"""
    db.cur.execute(q, (user_id, f_name, l_name, birth_year, school, level, gender, show))
    db.con.close()
    gc.collect()


def school_dropdown():
    # TODO: Store schools in a CSV or something nicer
    schools = ["Butler Fearon O'Connor", "Goggin Carrol", "Doyle Corrigan"]
    choices = list()
    for school in schools:
        choices.append((school, school))
    return choices


def year_dropdown():
    curr_year = dt.datetime.now().year
    choices = list()
    for i in range(curr_year, curr_year-100-1, -1):
        choices.append((str(i), str(i)))
    return choices


def get_feiseanna_with_forg(forg_id):
    db = Database()
    db.cur.execute("SELECT * FROM `feiseanna` WHERE `forg` = %s", forg_id)
    res = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return res


def get_dancers_with_user(user_id):
    db = Database()
    db.cur.execute("SELECT * FROM `dancers` WHERE `user` = %s", user_id)
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


def display_name(email):
    """Returns a statement welcoming the user"""
    db = Database()
    q = "SELECT `fName`, `lName` FROM `users` WHERE `email` = %s"
    num_rows = db.cur.execute(q, email)
    if num_rows == 0:
        return ""
    res = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return "Welcome, " + res["fName"] + " " + res["lName"] + "!"


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


def sign_up(email, password, f_name, l_name):
    q = "INSERT INTO `users` (`email`, `password`, `fName`, `lName`) VALUES (%s, %s, %s, %s)"
    db = Database()
    db.cur.execute(q, (email, generate_password_hash(password), f_name, l_name))
    db.con.close()
    gc.collect()


def display_feis():
    return "<Insert cool 3-widget feis display>"


def display_all_feiseanna():
    return "<Insert cool display of all feiseanna info>"


def display_all_results():
    return "<Insert cool display of all results>"


def display_open_feiseanna():
    return "<Insert cool table showing all open feiseanna>"


def feis_name_from_id(feis_id):
    db = Database()
    q = "SELECT `name` FROM `feiseanna` WHERE `id` = %s"
    db.cur.execute(q, feis_id)
    name = db.cur.fetchone()['name']
    db.con.close()
    gc.collect()
    return name
