from database import Database
from werkzeug.security import generate_password_hash, check_password_hash
import gc
import re


"""  LOGIN/SIGN UP  """





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
