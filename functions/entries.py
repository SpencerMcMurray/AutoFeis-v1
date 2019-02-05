import gc
from database import Database


def parse_dancers_for_entries(dancers):
    """(list of dict of str:int) -> dict of str:list of str/(list of str)
    Takes the list of dancer ids, and their respective competition ids and formats it to make it easy for
    the HTML to parse.
    """
    db = Database()
    data = {'comps': list(), 'codes': list(), 'dancers': list(), 'schools': list()}
    comp_q = """SELECT `name`, `code` FROM `competition` WHERE `id` = %s"""
    dancer_q = """SELECT `fName`, `lName`, `school` FROM `dancer` WHERE `id` = %s AND `show` = %s"""
    for dancer in dancers:
        # Fetch data from competition, and dancer tables
        db.cur.execute(comp_q, dancer['competition'])
        comp = db.cur.fetchone()
        db.cur.execute(dancer_q, (dancer['dancerId'], 1))
        curr_dancer = db.cur.fetchone()
        if curr_dancer is not None:
            # Maintain format for the data dict
            if comp['code'] not in data["codes"]:
                data['comps'].append(comp['name'])
                data['codes'].append(comp['code'])
                data['dancers'].append([curr_dancer['fName'] + " " + curr_dancer['lName']])
                data['schools'].append([curr_dancer['school']])
            else:
                data['dancers'][-1].append(curr_dancer['fName'] + " " + curr_dancer['lName'])
                data['schools'][-1].append(curr_dancer['school'])
    db.con.close()
    gc.collect()
    return data


def get_entries_from_feis(feis_id):
    """(int) -> list of dict of str:obj
    Returns all the entries for all competitions for a given feis
    """
    db = Database()
    q = """SELECT `dancerId`, `competition` FROM `competitor` WHERE feis = %s ORDER BY `competition`"""
    db.cur.execute(q, feis_id)
    dancers = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return parse_dancers_for_entries(dancers)
