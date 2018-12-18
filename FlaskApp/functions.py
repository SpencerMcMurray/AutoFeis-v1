from database import Database
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import gc
import datetime as dt
import csv
import os


class Competition:
    def __init__(self, min_age, max_age, name, code, sex, level):
        self._data = [min_age, max_age, name, code, sex, level]

    def __str__(self):
        return str(self._data)

    def serialize(self):
        # Make sure its a copy
        return {"data": self._data[:]}

    def get_data(self):
        return self._data


def register(reg, feis_id, dancer_id):
    """(dict of str:dict of str:int, int, int) -> NoneType
    Registers all dancer ids to the given competition id
    """
    print(reg)
    db = Database()
    q = """INSERT INTO `competitor` (`dancerId`, `competition`, `feis`) VALUES (%s, %s, %s)"""
    for comp in reg:
        db.cur.execute(q, (dancer_id, comp, feis_id))
    db.con.close()
    gc.collect()


def get_all_comps_for_dancers(feis_id, dancers):
    """(int, list of dict of str:obj) -> dict of int:list of dict of str:str/int
    Gets all the competitions for each dancer that they can register for
    """
    comps = dict()
    db = Database()
    # Allows people who identify as 'Other' to choose from both Male and Female competitions
    q = """SELECT `id`, `name`, `code` FROM `competition` WHERE `feis` = %s AND `minAge` <= %s AND `maxAge` >= %s AND
    (LOCATE(%s, `level`) > 0 or `level` = 'All') AND (`genders` = %s OR `genders` = 'All' OR %s = 'Other')"""
    for dancer in dancers:
        age = dt.datetime.now().year - dancer['birthYear']
        db.cur.execute(q, (feis_id, age, age, dancer['level'], dancer['gender'], dancer['gender']))
        comps[dancer['id']] = db.cur.fetchall()
    return comps


def get_all_feiseanna():
    """() -> list of dict of str:obj
    Returns all open feiseanna from our database
    """
    db = Database()
    q = """SELECT * FROM `feiseanna` WHERE `isOpen` = 1"""
    db.cur.execute(q)
    feiseanna = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return feiseanna


def make_comp_from_data(data):
    return Competition(data[0], data[1], data[2], data[3], data[4], data[5])


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
    q = """INSERT INTO `competition` (`feis`, `name`, `code`, `minAge`, `maxAge`, `level`, `genders`) VALUES 
           (%s, %s, %s, %s, %s, %s, %s)"""
    for level in comps:
        for comp in comps[level]:
            comp_data = comp.get_data()
            db.cur.execute(q, (feis_id, comp_data[2], comp_data[3], comp_data[0], comp_data[1], comp_data[5],
                           comp_data[4]))
    db.con.close()
    gc.collect()


def upload_file(file, name, upload_folder):
    filename = str(name) + ".pdf"
    if file and allowed_file(filename):
        file.save(os.path.join(upload_folder, secure_filename(filename)))


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
            comps.append(Competition(prev_age, age, curr_name, curr_code, "All", name))
            prev_age = age + 1

        if prev_age == 0:
            curr_name = name + " Under " + str(end_age)
            curr_code = code + str(end_age) + affix
            comps.append(Competition(0, end_age, curr_name, curr_code, "All", name))

        curr_name = name + " Over " + str(end_age)
        curr_code = code + str(99) + affix
        comps.append(Competition(end_age+1, 99, curr_name, curr_code, "All", name))
    else:
        for age in range(start_age, end_age+1, step):
            b_name = "Boys " + name + " Under " + str(age)
            b_code = "B" + code + str(age) + affix
            g_name = "Girls " + name + " Under " + str(age)
            g_code = "G" + code + str(age) + affix
            comps += [Competition(prev_age, age, b_name, b_code, "Male", name),
                      Competition(prev_age, age, g_name, g_code, "Female", name)]
            prev_age = age + 1

        if prev_age == 0:
            b_name = "Boys " + name + " Under " + str(end_age)
            b_code = "B" + code + str(end_age) + affix
            g_name = "Girls " + name + " Under " + str(end_age)
            g_code = "G" + code + str(end_age) + affix
            comps += [Competition(0, end_age, b_name, b_code, "Male", name),
                      Competition(0, end_age, g_name, g_code, "Female", name)]

        b_name = "Boys " + name + " Over " + str(end_age)
        b_code = "B" + code + str(99) + affix
        g_name = "Girls " + name + " Over " + str(end_age)
        g_code = "G" + code + str(99) + affix
        comps += [Competition(end_age+1, 99, b_name, b_code, "Male", name),
                  Competition(end_age+1, 99, g_name, g_code, "Female", name)]
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
                comps.append(Competition(prev_age, age, curr_name, curr_code, "All", "Grades"))
                prev_age = age + 1

            if prev_age == 0:
                curr_name = name + " Under " + str(end_age) + " " + dance[0]
                curr_code = code + str(end_age) + dance[1]
                comps.append(Competition(0, end_age, curr_name, curr_code, "All", "Grades"))

            curr_name = name + " Over " + str(end_age) + " " + dance[0]
            curr_code = code + str(99) + dance[1]
            comps.append(Competition(end_age+1, 99, curr_name, curr_code, "All", "Grades"))
        else:
            for age in range(start_age, end_age+1, step):
                b_name = "Boys " + name + " Under " + str(age) + " " + dance[0]
                b_code = "B" + code + str(age) + dance[1]
                g_name = "Girls " + name + " Under " + str(age) + " " + dance[0]
                g_code = "G" + code + str(age) + dance[1]
                comps += [Competition(prev_age, age, b_name, b_code, "Male", "Grades"),
                          Competition(prev_age, age, g_name, g_code, "Female", "Grades")]
                prev_age = age + 1

            if prev_age == 0:
                b_name = "Boys " + name + " Under " + str(end_age) + " " + dance[0]
                b_code = "B" + code + str(end_age) + dance[1]
                g_name = "Girls " + name + " Under " + str(end_age) + " " + dance[0]
                g_code = "G" + code + str(end_age) + dance[1]
                comps += [Competition(0, end_age, b_name, b_code, "Male", "Grades"),
                          Competition(0, end_age, g_name, g_code, "Female", "Grades")]

            b_name = "Boys " + name + " Over " + str(end_age) + " " + dance[0]
            b_code = "B" + code + str(99) + dance[1]
            g_name = "Girls " + name + " Over " + str(end_age) + " " + dance[0]
            g_code = "G" + code + str(99) + dance[1]
            comps += [Competition(end_age+1, 99, b_name, b_code, "Male", "Grades"),
                      Competition(end_age+1, 99, g_name, g_code, "Female", "Grades")]
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
            if prev_age == 0:
                curr_name = "Mixed Under " + str(age)
            else:
                curr_name = str(prev_age) + " to " + str(age)
            curr_code = "U" + str(age)
            comps['Main'].append(Competition(prev_age, age, curr_name, curr_code, "All", "All"))
            prev_age = age + 1

        # If we didn't enter the loop, add a youngest comp
        if prev_age == 0:
            curr_name = "Mixed Under " + str(age_max)
            curr_code = "U" + str(age_max)
            comps['Main'].append(Competition(prev_age, age_max, curr_name, curr_code, "All", "All"))

        curr_name = "Mixed Over " + str(age_max)
        curr_code = "O" + str(age_max)
        comps['Main'].append(Competition(age_max+1, 99, curr_name, curr_code, "All", "All"))
    else:
        for age in range(start, age_max+1, step):
            if prev_age == 0:
                b_name = "Boys Under " + str(age)
                g_name = "Girls Under " + str(age)
            else:
                b_name = "Boys " + str(prev_age) + " to " + str(age)
                g_name = "Girls " + str(prev_age) + " to " + str(age)
            b_code = "BU" + str(age)
            g_code = "GU" + str(age)
            comps['Main'] += [Competition(prev_age, age, b_name, b_code, "Male", "All"),
                              Competition(prev_age, age, g_name, g_code, "Female", "All")]
            prev_age = age + 1

        # If we didn't enter the loop, add a youngest comp
        if prev_age == 0:
            b_name = "Boys Under " + str(age_max)
            b_code = "BU" + str(age_max)
            g_name = "Girls Under " + str(age_max)
            g_code = "GU" + str(age_max)
            comps['Main'] += [Competition(prev_age, age_max, b_name, b_code, "Male", "All"),
                              Competition(prev_age, age_max, g_name, g_code, "Female", "All")]

        b_name = "Boys Over " + str(age_max)
        b_code = "BO" + str(age_max)
        g_name = "Girls Over " + str(age_max)
        g_code = "GO" + str(age_max)
        comps['Main'] += [Competition(age_max+1, 99, b_name, b_code, "Male", "All"),
                          Competition(age_max+1, 99, g_name, g_code, "Female", "All")]
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
        comps['Figure'].append(Competition(info['start_age'][i], info['end_age'][i], name, code, sex, "All"))

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
                                    info['level'][i]))
    return comps


def make_tir_competitions(info):
    comps = {'Tir na nOg': []}
    for i in range(len(info['start_age'])):
        name = "Tir na nOg Under " + str(info['end_age'][i])
        code = "TNN" + str(info['end_age'][i])
        comps['Tir na nOg'].append(Competition(info['start_age'][i], info['end_age'][i], name, code, "All", "All"))
    return comps


def make_art_competitions(info):
    comps = {'Art': []}
    for i in range(len(info['start_age'])):
        code = "AR-" + str(i+1)
        sex = info['gender'][i].capitalize()
        comps['Art'].append(Competition(info['start_age'][i], info['end_age'][i], info['name'][i], code, sex, "All"))
    return comps


def make_special_competitions(info):
    comps = {'Special': []}
    for i in range(len(info['start_age'])):
        code = "SP-" + str(i+1)
        sex = info['gender'][i].capitalize()
        comps['Special'].append(Competition(info['start_age'][i], info['end_age'][i], info['name'][i], code, sex,
                                            info['level'][i]))
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


def display_name(email):
    """Returns a statement welcoming the user"""
    db = Database()
    q = "SELECT `name` FROM `users` WHERE `email` = %s"
    num_rows = db.cur.execute(q, email)
    if num_rows == 0:
        return ""
    res = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return "Welcome, " + res['name'] + "!"


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
    q = "INSERT INTO `users` (`email`, `password`, `name`) VALUES (%s, %s, %s)"
    db = Database()
    name = f_name + " " + l_name
    db.cur.execute(q, (email, generate_password_hash(password), name))
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
