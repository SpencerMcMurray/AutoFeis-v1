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


DANCERS_PER_PAGE = 17


class Competition:
    def __init__(self, min_age, max_age, name, code, sex, level, dance):
        self._data = [min_age, max_age, name, code, sex, level, dance]

    def __str__(self):
        return str(self._data)

    def serialize(self):
        # Make sure its a hard copy
        return {"data": self._data[:]}

    def get_data(self):
        return self._data


"""  COMPETITION EDITOR  """


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
    delete_comp(comp['id'])

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
    delete_comp(comp['id'])

    db.con.close()
    gc.collect()


def delete_comp(comp_id):
    """(int) -> NoneType
    Deletes the competition with the given id
    """
    db = Database()
    q = """DELETE FROM `competition` WHERE `id` = %s"""
    db.cur.execute(q, comp_id)
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
    delete_comp(other_id)


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


def get_comp_from_id(comp_id):
    """(int) -> dict of str:obj
    Returns the corresponding competition to the id given
    """
    db = Database()
    q = """SELECT * FROM `competition` WHERE `id` = %s"""
    db.cur.execute(q, comp_id)
    comp = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return comp


def get_open_from_id(feis_id):
    """(int) -> bool
    Returns the isOpen value for the feis with the given id
    """
    db = Database()
    q = """SELECT `isOpen` FROM `feiseanna` WHERE `id` = %s"""
    db.cur.execute(q, feis_id)
    open = db.cur.fetchone()['isOpen']
    db.con.close()
    gc.collect()
    return bool(open)


def get_all_clopen_feiseanna(is_open):
    """(bool) -> list of dict of str:obj
    Gets all open feiseanna
    """
    db = Database()
    q = """SELECT * FROM `feiseanna` WHERE `isOpen` = %s ORDER BY `date` ASC"""
    db.cur.execute(q, int(is_open))
    feiseanna = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return feiseanna


"""  SCORESHEET CALCULATOR  """


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


def get_comps_from_feis_id(feis_id):
    """(int) -> list of dict of str:obj
    Gets all competitions associated with the given feis id
    """
    db = Database()
    q = """SELECT `id`, `name`, `code` FROM `competition` WHERE `feis` = %s ORDER BY `dance`, `level`, `minAge`"""
    db.cur.execute(q, feis_id)
    comps = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return comps


def get_latest_three_feiseanna():
    """() -> list of dict of str:str
    Returns the 3 most upcoming feiseanna
    """
    db = Database()
    q = """SELECT * FROM `feiseanna` ORDER BY `date` ASC LIMIT 3"""
    db.cur.execute(q)
    feiseanna = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return feiseanna


"""  ENTRIES  """


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


"""  REGISTRATION  """


def register(reg, feis_id, dancer_id):
    """(dict of str:dict of str:int, int, int) -> NoneType
    Registers all dancer ids to the given competition id
    """
    db = Database()
    q = """INSERT INTO `competitor` (`dancerId`, `competition`, `feis`) VALUES (%s, %s, %s)"""
    for comp in reg:
        db.cur.execute(q, (dancer_id, comp, feis_id))
    db.con.close()
    gc.collect()


def get_all_comps_for_dancers(feis_id, dancers):
    """(int, list of dict of str:obj) -> dict of int:list of dict of str:str/int
    Gets all the competitions for each dancer that they can register for.
    Excludes competitions which they are already registered for.
    """
    comps = dict()
    db = Database()
    # Allows people who identify as 'Other' to choose from both Male and Female competitions
    q = """SELECT `id`, `name`, `code` FROM `competition` WHERE `feis` = %s AND `minAge` <= %s AND `maxAge` >= %s AND
    (LOCATE(%s, `level`) > 0 OR `level` = 'All' OR (%s = 'Grades' AND `level` IN
    ('Beginner', 'Advanced Beginner', 'Novice', 'Open Prizewinner'))) AND (`genders` = %s OR `genders` = 'All'
    OR %s = 'Other') AND `id` NOT IN (SELECT `competition` FROM `competitor` WHERE `dancerId` = %s)"""
    for dancer in dancers:
        age = dt.datetime.now().year - dancer['birthYear']
        db.cur.execute(q, (feis_id, age, age, dancer['level'], dancer['level'], dancer['gender'], dancer['gender'],
                           dancer['id']))
        comps[dancer['id']] = db.cur.fetchall()
    return comps


def get_all_feiseanna():
    """() -> list of dict of str:obj
    Returns all feiseanna from our database ordered by date
    """
    db = Database()
    q = """SELECT * FROM `feiseanna` ORDER BY `date` DESC"""
    db.cur.execute(q)
    feiseanna = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return feiseanna


"""  FEIS CREATION  """


def make_comp_from_data(data):
    return Competition(data[0], data[1], data[2], data[3], data[4], data[5], data[6])


def deserialize_comps(comps):
    """(dict of str:list of dict) -> dict of str:list of Competition
    Allows for serialized comps to be be turned back into comps"""
    # Make a copy so we dont mutate the original
    new_comps = dict()
    for key in comps:
        new_comps[key] = list()
        for comp in range(len(comps[key])):
            new_comps[key].append(make_comp_from_data(comps[key][comp]["data"]))
    return new_comps


def serialize_comps(comps):
    """(dict of str:list of Competition) -> dict of str:list of dict
    Allows for comps dict to be put into a session"""
    # Make a copy so we dont mutate the original
    new_comps = dict()
    for key in comps:
        new_comps[key] = list()
        for comp in range(len(comps[key])):
            new_comps[key].append(comps[key][comp].serialize())
    return new_comps


def create_comps(feis_id, comps):
    db = Database()
    q = """INSERT INTO `competition` (`feis`, `name`, `code`, `minAge`, `maxAge`, `level`, `genders`, `dance`) VALUES 
           (%s, %s, %s, %s, %s, %s, %s, %s)"""
    for level in comps:
        for comp in comps[level]:
            comp_data = comp.get_data()
            db.cur.execute(q, (feis_id, comp_data[2], comp_data[3], comp_data[0], comp_data[1], comp_data[5],
                           comp_data[4], comp_data[6]))
    db.con.close()
    gc.collect()


def upload_file(file, name, upload_folder):
    filename = str(name) + ".pdf"
    if file and allowed_file(filename):
        file.save(os.path.join(upload_folder, secure_filename(filename)))


def set_defaults_for_feis(feis, form):
    """(dict of str:obj) -> Form
    Creates a feis form with all defaults set to current feis data
    """
    form.name.default = feis['name']
    form.location.default = feis['location']
    form.region.default = feis['region']
    form.website.default = feis['website']
    form.process()
    return form


def update_feis(feis_id, name, date, location, region, website):
    db = Database()
    q = """UPDATE `feiseanna` SET `name` = %s, `date` = %s, `location` = %s, `region` = %s, `website` = %s WHERE
           `id` = %s"""
    db.cur.execute(q, (name, date, location, region, website, feis_id))
    db.con.close()
    gc.collect()


def create_feis(forg, name, date, location, region, website):
    db = Database()
    q = """INSERT INTO `feiseanna` (`forg`, `name`, `date`, `location`, `region`, `isOpen`, `website`, `syllabus`)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    db.cur.execute(q, (forg, name, date, location, region, 1, website, ""))
    feis_id = db.con.insert_id()
    q = """UPDATE feiseanna SET `syllabus` = %s WHERE `id` = %s"""
    db.cur.execute(q, (str(feis_id) + ".pdf", feis_id))
    db.con.close()
    gc.collect()
    return feis_id


def get_regions():
    with open("static/csv/regions.csv", 'r') as my_file:
        reader = csv.reader(my_file, delimiter='\t')
        regions = list()
        for row in list(reader):
            regions.append((row[0], row[0]))
        return regions


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'


def make_champ_comps(start_age, end_age, step, name, code, affix, boys):
    comps = []
    prev_age = 0
    if boys is None:
        for age in range(start_age, end_age+1, step):
            curr_name = name + " Under " + str(age)
            curr_code = code + str(age) + affix
            comps.append(Competition(prev_age, age, curr_name, curr_code, "All", name, name))
            prev_age = age + 1

        if prev_age == 0:
            curr_name = name + " Under " + str(end_age)
            curr_code = code + str(end_age) + affix
            comps.append(Competition(0, end_age, curr_name, curr_code, "All", name, name))

        curr_name = name + " Over " + str(end_age)
        curr_code = code + str(99) + affix
        comps.append(Competition(end_age+1, 99, curr_name, curr_code, "All", name, name))
    else:
        for age in range(start_age, end_age+1, step):
            b_name = "Boys " + name + " Under " + str(age)
            b_code = "B" + code + str(age) + affix
            g_name = "Girls " + name + " Under " + str(age)
            g_code = "G" + code + str(age) + affix
            comps += [Competition(prev_age, age, b_name, b_code, "Male", name, name),
                      Competition(prev_age, age, g_name, g_code, "Female", name, name)]
            prev_age = age + 1

        if prev_age == 0:
            b_name = "Boys " + name + " Under " + str(end_age)
            b_code = "B" + code + str(end_age) + affix
            g_name = "Girls " + name + " Under " + str(end_age)
            g_code = "G" + code + str(end_age) + affix
            comps += [Competition(0, end_age, b_name, b_code, "Male", name, name),
                      Competition(0, end_age, g_name, g_code, "Female", name, name)]

        b_name = "Boys " + name + " Over " + str(end_age)
        b_code = "B" + code + str(99) + affix
        g_name = "Girls " + name + " Over " + str(end_age)
        g_code = "G" + code + str(99) + affix
        comps += [Competition(end_age+1, 99, b_name, b_code, "Male", name, name),
                  Competition(end_age+1, 99, g_name, g_code, "Female", name, name)]
    return comps


def make_grades_comps(start_age, end_age, step, name, code, boys, dance_and_code):
    # dance_and_code is a 2D array in the form [[name, code],...]
    comps = []
    for dance in dance_and_code:
        prev_age = 0
        if boys is None:
            for age in range(start_age, end_age+1, step):
                curr_name = name + " Under " + str(age) + " " + dance[0]
                curr_code = code + str(age) + dance[1]
                comps.append(Competition(prev_age, age, curr_name, curr_code, "All", name, dance[0]))
                prev_age = age + 1

            if prev_age == 0:
                curr_name = name + " Under " + str(end_age) + " " + dance[0]
                curr_code = code + str(end_age) + dance[1]
                comps.append(Competition(0, end_age, curr_name, curr_code, "All", name, dance[0]))

            curr_name = name + " Over " + str(end_age) + " " + dance[0]
            curr_code = code + str(99) + dance[1]
            comps.append(Competition(end_age+1, 99, curr_name, curr_code, "All", name, dance[0]))
        else:
            for age in range(start_age, end_age+1, step):
                b_name = "Boys " + name + " Under " + str(age) + " " + dance[0]
                b_code = "B" + code + str(age) + dance[1]
                g_name = "Girls " + name + " Under " + str(age) + " " + dance[0]
                g_code = "G" + code + str(age) + dance[1]
                comps += [Competition(prev_age, age, b_name, b_code, "Male", name, dance[0]),
                          Competition(prev_age, age, g_name, g_code, "Female", name, dance[0])]
                prev_age = age + 1

            if prev_age == 0:
                b_name = "Boys " + name + " Under " + str(end_age) + " " + dance[0]
                b_code = "B" + code + str(end_age) + dance[1]
                g_name = "Girls " + name + " Under " + str(end_age) + " " + dance[0]
                g_code = "G" + code + str(end_age) + dance[1]
                comps += [Competition(0, end_age, b_name, b_code, "Male", name, dance[0]),
                          Competition(0, end_age, g_name, g_code, "Female", name, dance[0])]

            b_name = "Boys " + name + " Over " + str(end_age) + " " + dance[0]
            b_code = "B" + code + str(99) + dance[1]
            g_name = "Girls " + name + " Over " + str(end_age) + " " + dance[0]
            g_code = "G" + code + str(99) + dance[1]
            comps += [Competition(end_age+1, 99, b_name, b_code, "Male", name, dance[0]),
                      Competition(end_age+1, 99, g_name, g_code, "Female", name, dance[0])]
    return comps


def make_main_competitions(single_ages, boys_champ, boys_grades,
                           champ_max, prelim_max, set_max, grades_max):
    """Makes the main competitions given the data obtained from asking to the feis organizer"""
    step = (1 if single_ages is not None else 2)
    start = (4 if single_ages is not None else 5)

    # Make all our main competitions
    comps = {'Open Championship': make_champ_comps(start, champ_max, step, "Open Championship", "C", "", boys_champ),
             'Preliminary Championship': make_champ_comps(start, prelim_max, step, "Preliminary Championship", "PC",
                                                          "", boys_champ),
             'Preliminary Championship Set': make_champ_comps(start, set_max, step, "Preliminary Championship Set",
                                                              "PC", "S", boys_champ),
             'Open Prizewinner': make_grades_comps(start, grades_max, step, "Open Prizewinner", "P", boys_grades,
                                                   [["Reel", "R"], ["Slip Jig", "S"], ["Treble Jig", "T"],
                                                    ["Hornpipe", "H"], ["Traditional Set", "D"],
                                                    ["Contemporary Set", "C"]]),
             'Novice': make_grades_comps(start, grades_max, step, "Novice", "N", boys_grades,
                                         [["Reel", "R"], ["Light Jig", "L"], ["Slip Jig", "S"],
                                          ["Treble Jig", "T"], ["Hornpipe", "H"], ["Traditional Set", "D"]]),
             'Advanced Beginner': make_grades_comps(start, grades_max, step, "Advanced Beginner", "A", boys_grades,
                                                    [["Reel", "R"], ["Light Jig", "L"], ["Single Jig", "X"],
                                                     ["Slip Jig", "S"], ["Treble Jig", "T"], ["Hornpipe", "H"],
                                                     ["Traditional Set", "D"]]),
             'Beginner':  make_grades_comps(start, grades_max, step, "Beginner", "B", boys_grades,
                                            [["Reel", "R"], ["Light Jig", "L"], ["Single Jig", "X"],
                                             ["Slip Jig", "S"]])}
    return comps


def make_main_major_competitions(single_ages, boys, age_max):
    step = (1 if single_ages is not None else 2)
    start = (4 if single_ages is not None else 5)

    comps = {'Main': []}
    prev_age = 0
    if not boys:
        for age in range(start, age_max+1, step):
            curr_name = "Mixed Under " + str(age)
            curr_code = "U" + str(age)
            comps['Main'].append(Competition(prev_age, age, curr_name, curr_code, "All", "All", "Main"))
            prev_age = age + 1

        # If we didn't enter the loop, add a youngest comp
        if prev_age == 0:
            curr_name = "Mixed Under " + str(age_max)
            curr_code = "U" + str(age_max)
            comps['Main'].append(Competition(prev_age, age_max, curr_name, curr_code, "All", "All", "Main"))

        curr_name = "Mixed Over " + str(age_max)
        curr_code = "O" + str(age_max)
        comps['Main'].append(Competition(age_max+1, 99, curr_name, curr_code, "All", "All", "Main"))
    else:
        for age in range(start, age_max+1, step):
            b_name = "Boys Under " + str(age)
            g_name = "Girls Under " + str(age)
            b_code = "BU" + str(age)
            g_code = "GU" + str(age)
            comps['Main'] += [Competition(prev_age, age, b_name, b_code, "Male", "All", "Main"),
                              Competition(prev_age, age, g_name, g_code, "Female", "All", "Main")]
            prev_age = age + 1

        # If we didn't enter the loop, add a youngest comp
        if prev_age == 0:
            b_name = "Boys Under " + str(age_max)
            b_code = "BU" + str(age_max)
            g_name = "Girls Under " + str(age_max)
            g_code = "GU" + str(age_max)
            comps['Main'] += [Competition(prev_age, age_max, b_name, b_code, "Male", "All", "Main"),
                              Competition(prev_age, age_max, g_name, g_code, "Female", "All", "Main")]

        b_name = "Boys Over " + str(age_max)
        b_code = "BO" + str(age_max)
        g_name = "Girls Over " + str(age_max)
        g_code = "GO" + str(age_max)
        comps['Main'] += [Competition(age_max+1, 99, b_name, b_code, "Male", "All", "Main"),
                          Competition(age_max+1, 99, g_name, g_code, "Female", "All", "Main")]
    return comps


def make_figure_competitions(info):
    comps = {'Figure': []}
    for i in range(len(info['start_age'])):
        name = "Figure "
        if int(info['end_age'][i]) == 99:
            name += "Over " + str(info['start_age'][i])
        else:
            name += "Under " + str(info['end_age'][i])
        code = "FG" + str(info['end_age'][i])
        sex = "All"
        name = str(info['type'][i]) + "-Hand " + name
        code = str(info['type'][i]) + "-" + code
        if info['gender'][i] == 'male':
            code += "M"
            name = "Boys " + name
            sex = "Male"
        elif info['gender'][i] == 'female':
            code += "F"
            name = "Girls " + name
            sex = "Female"
        elif info['gender'][i] == 'mixed':
            code += "X"
            name = "Mixed " + name
        comps['Figure'].append(Competition(info['start_age'][i], info['end_age'][i], name, code, sex, "All", "Figure"))
    return comps


def make_treble_competitions(info):
    comps = {'Treble Reel': []}
    for i in range(len(info['start_age'])):
        name = ""
        code = ""
        if info['level'][i] != "All":
            name = info['level'][i] + " "
            code = info['level'][i][0]
        gender = info['gender'][i]
        sex = "All"
        if gender == "female":
            name += "Girls "
            code = "G" + code
            sex = "Female"
        elif gender == "male":
            name += "Boys "
            code = "B" + code
            sex = "Male"
        name += "Treble Reel "
        code += "TR"
        if int(info['end_age'][i]) == 99:
            name += "Over " + str(info['start_age'][i])
            code += "99"
        else:
            name += "Under " + str(info['end_age'][i])
            code += str(info['end_age'][i])
        comps['Treble Reel'].append(Competition(info['start_age'][i], info['end_age'][i], name, code, sex,
                                    info['level'][i], "Treble"))
    return comps


def make_tir_competitions(info):
    comps = {'Tir na nOg': []}
    for i in range(len(info['start_age'])):
        if int(info['end_age'][i]) == 99:
            name = "Tir na nOg Over " + str(info['start_age'][i])
            code = "TNN" + str(info['end_age'][i])
        else:
            name = "Tir na nOg Under " + str(info['end_age'][i])
            code = "TNN" + str(info['end_age'][i])
        comps['Tir na nOg'].append(Competition(info['start_age'][i], info['end_age'][i], name, code, "All", "All",
                                               "Tir"))
    return comps


def make_art_competitions(info):
    comps = {'Art': []}
    for i in range(len(info['start_age'])):
        code = "AR-" + str(i+1)
        sex = info['gender'][i].capitalize()
        comps['Art'].append(Competition(info['start_age'][i], info['end_age'][i], info['name'][i], code, sex, "All",
                                        "Art"))
    return comps


def make_special_competitions(info):
    comps = {'Special': []}
    for i in range(len(info['start_age'])):
        code = "SP-" + str(i+1)
        sex = info['gender'][i].capitalize()
        comps['Special'].append(Competition(info['start_age'][i], info['end_age'][i], info['name'][i], code, sex,
                                            info['level'][i], "Special"))
    return comps


def get_comps_from_session(session):
    # TODO: Allow for much deeper customization
    comps = dict()
    if session['include_levels'] is None:
        # Checks if either boys champ or boys grades is checked
        boys = session['boys_champ'] is not None or session['boys_grades'] is not None
        mains = make_main_major_competitions(session['single_ages'], boys, session['main_max'])
    else:
        mains = make_main_competitions(session['single_ages'], session['boys_champ'],
                                       session['boys_grades'], session['champ_max'], session['prelim_max'],
                                       session['set_max'], session['grades_max'])
    comps.update(mains)

    # Get all our extra competitions
    figures = make_figure_competitions(session['FG_info'])
    comps.update(figures)

    trebles = make_treble_competitions(session['TR_info'])
    comps.update(trebles)

    tir = make_tir_competitions(session['TNN_info'])
    comps.update(tir)

    art = make_art_competitions(session['AR_info'])
    comps.update(art)

    special = make_special_competitions(session['SP_info'])
    comps.update(special)
    return comps


def get_dancer_from_id(dancer_id):
    db = Database()
    q = "SELECT * FROM `dancer` WHERE `id` = %s"
    db.cur.execute(q, dancer_id)
    dancer = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return dancer


def delete_dancer_from_id(uid):
    db = Database()
    q = "DELETE FROM `dancer` WHERE `id` = %s"
    db.cur.execute(q, (uid,))
    db.con.close()
    gc.collect()


"""  DANCER CREATION  """


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


def alter_dancer(dancer_id, f_name, l_name, school, birth_year, level, gender, show):
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
