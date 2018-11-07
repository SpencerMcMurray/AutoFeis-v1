from database import Database
from werkzeug.security import generate_password_hash, check_password_hash
from gc import collect


def validate(email, password):
    """Returns True iff password is valid for given email"""
    db = Database()
    q = "SELECT * FROM users WHERE email = %s"
    num_rows = db.cur.execute(q, email)
    if num_rows == 0:
        return False
    res = db.cur.fetchone()
    db.con.close()
    collect()
    return check_password_hash(res["password"], password)


def email_taken(email):
    """Returns True iff the email given exists in the database"""
    db = Database()
    q = "SELECT email FROM users WHERE email = %s"
    num_rows = db.cur.execute(q, (email,))
    db.con.close()
    collect()
    return num_rows != 0


def sign_up(email, password, f_name, l_name):
    q = "INSERT INTO users (email, password, fName, lName) VALUES (%s, %s, %s, %s)"
    db = Database()
    db.cur.execute(q, (email, generate_password_hash(password), f_name, l_name))
    db.con.commit()
    db.con.close()
    collect()


def display_feis():
    return "<Insert cool 3-widget feis display>"


def display_all_feiseanna():
    return "<Insert cool display of all feiseanna info>"


def display_all_results():
    return "<Insert cool display of all results>"


def display_open_feiseanna():
    return "<Insert cool table showing all open feiseanna>"


def display_my_dancers():
    return "<Insert cool table with all my dancers>"


def display_my_feiseanna():
    return "<Insert cool table with all my feiseanna>"


def feis_functions_html(feis_id):
    # TODO: Query the database
    html = """
    {% extends "outline.html" %}
    {% block body %}
        <body>
        <style>
            th, td {
                text-align:center;
                padding: 15px;
                border: 2px solid black;
            }
            table tr:nth-child(odd) {
                background-color: #eee;
            }
            table tr:nth-child(even) {
                background-color: #fff;
            }
        </style><br>
        <b style='font-size:20px;'>What would you like to do with {$name}?</b><hr>
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
    return html
