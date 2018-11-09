from database import Database
from werkzeug.security import generate_password_hash, check_password_hash
import gc


def get_feiseanna_with_forg(forg_id):
    db = Database()
    db.cur.execute("SELECT * FROM feiseanna WHERE forg = %s", forg_id)
    res = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return res


def get_dancers_with_user(user_id):
    db = Database()
    db.cur.execute("SELECT * FROM dancers WHERE user = %s", user_id)
    res = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return res


def get_id_from_email(email):
    db = Database()
    num_rows = db.cur.execute("SELECT id FROM users WHERE email = %s", email)
    if num_rows > 0:
        return db.cur.fetchone()['id']
    return -1


def display_name(email):
    """Returns a statement welcoming the user"""
    db = Database()
    q = "SELECT fName, lName FROM users WHERE email = %s"
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
    q = "SELECT * FROM users WHERE email = %s"
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
    q = "SELECT email FROM users WHERE email = %s"
    num_rows = db.cur.execute(q, (email,))
    db.con.close()
    gc.collect()
    return num_rows != 0


def sign_up(email, password, f_name, l_name):
    q = "INSERT INTO users (email, password, fName, lName) VALUES (%s, %s, %s, %s)"
    db = Database()
    db.cur.execute(q, (email, generate_password_hash(password), f_name, l_name))
    db.con.commit()
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


def feis_functions_html(feis_id):
    db = Database()
    q = "SELECT name FROM feiseanna WHERE id = %s"
    db.cur.execute(q, feis_id)
    feis = db.cur.fetchone()
    html = """
    {% extends "outline.html" %}
    {% block body %}
        <body><br>
        <b style='font-size:20px;'>What would you like to do with """ + feis['name'] + """?</b><hr>
        <table style='margin:0px auto;text-align:center;font-size:20px;border:2px solid black;width 100%;'>
            <tr>
                <td>
                    Edit Feis Info
                </td>
            </tr>
            <tr>
                <td>
                    Combine/Split Competitions
                </td>
            </tr>
            <tr>
                <td>
                    Scoresheet Calculator
                </td>
            </tr>
        </table>
        </body>
    {% endblock body %}
    """
    db.con.close()
    gc.collect()
    return html
