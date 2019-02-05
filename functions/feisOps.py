import gc
import math
from database import Database


DANCERS_PER_PAGE = 17


def get_sheets_for_comps(comps):
    """(list of dict of str:obj) -> list of dict of str:obj
    Calculates the number of scoresheets per judge for each competitions based on entries
    """
    db = Database()
    q = """SELECT `feis` FROM `competitor` WHERE `competition` = %s"""
    data = list()
    total = 0
    for comp in comps:
        db.cur.execute(q, comp['id'])
        entries = len(db.cur.fetchall())

        # You need one sheet for every(up to) 17 dancers
        entries = math.ceil(entries/DANCERS_PER_PAGE)
        total += entries
        data.append({'name': comp['name'], 'code': comp['code'], 'entries': entries})
    db.con.close()
    gc.collect()
    return data, total
