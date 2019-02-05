import math
import gc
import re
import datetime as dt
import random as rnd
import databaseOps as ops
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


def nested_empty_lists(in_list):
    """(list( of list)* of dict of str:obj) -> bool
    Recursively returns True iff all nested lists are empty
    """
    if not isinstance(in_list, list):
        return False
    if isinstance(in_list, list) and len(in_list) == 0:
        return True
    # Else in_list is a list, and it has at least one element
    ret_bool = True
    i = 0
    while ret_bool and i < len(in_list):
        ret_bool = ret_bool and nested_empty_lists(in_list[i])
        i += 1
    return ret_bool


def make_titles_tables_for(feis_id, comp_type):
    """(int, str) -> list of str, list of list of dict of str:obj
    Makes all the titles for the tables, and also fetches all the competitions necessary for each type
    """
    db = Database()
    comps = list()
    if comp_type == "Main":
        levels = ["Open Championship", "Preliminary Championship", "Preliminary Championship Set", "Beginner",
                  "Advanced Beginner", "Novice", "Open Prizewinner"]
        q = """SELECT * FROM `competition` WHERE `level` = %s AND `feis` = %s ORDER BY `dance`, `level`, `minAge`"""
        for level in levels:
            db.cur.execute(q, (level, feis_id))
            comps.append(db.cur.fetchall())
        if nested_empty_lists(comps):
            q = """SELECT * FROM `competition` WHERE `dance` = %s AND `feis` = %s ORDER BY `dance`, `level`, `minAge`"""
            db.cur.execute(q, "Main")
            comps.clear()
            levels.clear()
            levels.append("Main")
            comps.append(db.cur.fetchall())
        return levels, comps
    levels = [comp_type]
    q = """SELECT * FROM `competition` WHERE `dance` = %s AND `feis` = %s ORDER BY `dance`, `level`, `minAge`"""
    db.cur.execute(q, (comp_type.split(' ')[0], feis_id))
    comps.append(db.cur.fetchall())
    return levels, comps


"""  SPLIT COMPETITIONS  """


def update_name(name, age):
    """(str, int) -> str
    Updates the name if needed
    """
    if name.find('Over') > 0:
        name = re.sub("\\d+", str(age - 1), name)
    return name


def split_by_age(comp, age):
    """(dict of str:obj, int) -> NoneType
    Splits the competition given in two new comps split by age
    """
    db = Database()
    q = """INSERT INTO `competition` (`feis`, `name`, `code`, `minAge`, `maxAge`, `level`, `genders`, `dance`) VALUES
           (%s, %s, %s, %s, %s, %s, %s, %s)"""
    # Create two competitions split by age
    db.cur.execute(q, (comp['feis'], comp['name'], comp['code'], comp['minAge'], age - 1, comp['level'],
                       comp['genders'], comp['dance']))
    id_young = db.cur.lastrowid
    db.cur.execute(q, (comp['feis'], comp['name'], comp['code'], age, comp['maxAge'], comp['level'], comp['genders'],
                       comp['dance']))
    id_old = db.cur.lastrowid
    update_names_with_age(id_young, id_old)

    # Gather all competitor info and assign them the correct competition
    q = """SELECT `id`, `dancerId` FROM `competitor` WHERE `competition` = %s"""
    db.cur.execute(q, comp['id'])
    competitors = db.cur.fetchall()
    q = """UPDATE `competitor` SET `competition` = %s WHERE `id` = %s"""
    dancer_q = """SELECT `birthYear` FROM `dancer` WHERE `id` = %s"""
    for competitor in competitors:
        db.cur.execute(dancer_q, competitor['dancerId'])
        dancer = db.cur.fetchone()
        if dt.datetime.now().year - dancer['birthYear'] >= age:
            db.cur.execute(q, (id_old, competitor['id']))
        else:
            db.cur.execute(q, (id_young, competitor['id']))

    # Remove the original competition
    ops.delete_comp(comp['id'])

    db.con.close()
    gc.collect()


def update_names_with_age(id_young, id_old):
    """(int, int, int) -> NoneType
    Updates the name to reflect the competitions new properties
    """
    db = Database()
    grab_q = """SELECT * FROM `competition` WHERE `id` = %s"""
    update_q = """UPDATE `competition` SET `name` = %s, `code` = %s WHERE `id` = %s"""

    # Update younger competition
    db.cur.execute(grab_q, id_young)
    comp = db.cur.fetchone()
    name = comp['name'].replace('Over', 'Under')
    code = comp['code']
    if comp['dance'] == "Main":
        code = code.replace('O', 'U')

    # Use a regex to change the old age in the name and code to the new age
    name = re.sub("\\d+", str(comp['maxAge']), name)
    code = re.sub("\\d+", str(comp['maxAge']), code)
    db.cur.execute(update_q, (name, code, id_young))

    # Update older competition
    db.cur.execute(grab_q, id_old)
    comp = db.cur.fetchone()
    name = comp['name']
    code = comp['code']
    if name.count('Over') > 0:
        name = re.sub("\\d+", str(comp['minAge'] - 1), name)
        if comp['dance'] == "Main":
            code = re.sub("\\d+", str(comp['minAge'] - 1), code)
    db.cur.execute(update_q, (name, code, id_old))

    db.con.close()
    gc.collect()


def split_into_ab(comp):
    """(dict of str:obj) -> NoneType
    Splits the competition given in two equal, randomly distributed new comps.
    """
    db = Database()

    # Make two new competitions which are identical, but called A and B
    q = """INSERT INTO `competition` (`feis`, `name`, `code`, `minAge`, `maxAge`, `level`, `genders`, `dance`) VALUES
           (%s, %s, %s, %s, %s, %s, %s, %s)"""
    name_a = comp['name'] + " A"
    code_a = comp['code'] + "A"
    name_b = comp['name'] + " B"
    code_b = comp['code'] + "B"

    db.cur.execute(q, (comp['feis'], name_a, code_a, comp['minAge'], comp['maxAge'], comp['level'],
                       comp['genders'], comp['dance']))
    id_a = db.cur.lastrowid
    db.cur.execute(q, (comp['feis'], name_b, code_b, comp['minAge'], comp['maxAge'], comp['level'],
                       comp['genders'], comp['dance']))
    id_b = db.cur.lastrowid

    # Gather all the competitors in the original competition and assign them a new comp
    q = """SELECT `id` FROM `competitor` WHERE `competition` = %s"""
    db.cur.execute(q, comp['id'])
    dancers = db.cur.fetchall()
    q = """UPDATE `competitor` SET `competition` = %s WHERE `id` = %s"""
    push_a = True
    size = len(dancers)
    for i in range(size):
        # Get a random index to use
        r = rnd.randrange(len(dancers))
        if push_a:
            db.cur.execute(q, (id_a, dancers[r]['id']))
        else:
            db.cur.execute(q, (id_b, dancers[r]['id']))
        dancers.pop(r)
        push_a = not push_a

    # Remove the original competition
    ops.delete_comp(comp['id'])

    db.con.close()
    gc.collect()


"""  MERGE COMPETITIONS  """


def merge_comps(comp_id, other_id):
    """(int, int) -> NoneType
    Merges the two competitions into one
    Note: comp_id is the id of the competition with the greater maxAge
    Note: Merging a senior comp with a junior comp(minAge=0) results in a name with 'Over -1'
    """
    update_competitor_comp(comp_id, other_id)
    update_min_age(comp_id, other_id)
    db = Database()
    q = """SELECT * FROM `competition` WHERE `id` = %s"""
    db.cur.execute(q, comp_id)
    comp = db.cur.fetchone()
    # If the competition is a senior comp update the over to account for the new min age
    if comp['maxAge'] == 99:
        q = """UPDATE `competition` SET `name` = %s, `code` = %s WHERE `id` = %s"""
        name = re.sub("\\d+", str(comp['minAge'] - 1), comp['name'])
        code = comp['code']
        if comp['dance'] == "Main":
            code = re.sub("\\d+", str(comp['minAge'] - 1), comp['code'])
        db.cur.execute(q, (name, code, comp_id))
    db.con.close()
    gc.collect()
    ops.delete_comp(other_id)


def update_min_age(comp_id, other_id):
    """(int, int) -> NoneType
    Updates the min age of the first comp with the min age of the second
    """
    db = Database()
    min_q = """SELECT `minAge` FROM `competition` WHERE `id` = %s"""
    db.cur.execute(min_q, other_id)
    comp = db.cur.fetchone()
    min_age = comp['minAge']
    update_q = """UPDATE `competition` SET `minAge` = %s WHERE `id` = %s"""
    db.cur.execute(update_q, (min_age, comp_id))
    db.con.close()
    gc.collect()


def update_competitor_comp(comp_id, other_id):
    """(int, int) -> NoneType
    Updates all the competitors in the other comp to be in the new comp
    """
    db = Database()
    q = """UPDATE `competitor` SET `competition` = %s WHERE `competition` = %s"""
    db.cur.execute(q, (comp_id, other_id))
    db.con.close()
    gc.collect()


def get_mergeable_comps(comp):
    """(dict of str:obj) -> list of dict of str:obj
    Returns all the competitions that are able to merge with the given competition
    """
    db = Database()
    q = """SELECT * FROM `competition` WHERE `level` = %s AND (`maxAge` = %s OR `minAge` = %s OR `maxAge` = %s
           OR `minAge` = %s) AND NOT `id` = %s AND `feis` = %s AND `dance` = %s AND `genders` = %s"""
    # These are to check if the competition's min/max will line up with our max/min
    under_max = comp['minAge'] - 1
    over_min = comp['maxAge'] + 1
    db.cur.execute(q, (comp['level'], under_max, over_min, comp['maxAge'], comp['minAge'], comp['id'], comp['feis'],
                       comp['dance'], comp['genders']))
    comps = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return comps

