from database import Database
from werkzeug.security import generate_password_hash, check_password_hash
import gc
import datetime as dt


class Competition:
    def __init__(self, min_age, max_age, name, code, sex, level):
        self._data = [min_age, max_age, name, code, sex, level]

    def __str__(self):
        return str(self._data)

    def get_data(self):
        return self._data


def make_champ_comps(start_age, end_age, step, name, code, affix, boys):
    comps = []
    prev_age = 0
    if boys is None:
        for age in range(start_age, end_age+1, step):
            curr_name = name + " Under " + str(age)
            curr_code = code + str(age) + affix
            comps.append(Competition(prev_age, age, curr_name, curr_code, "All", code))
            prev_age = age + 1
        curr_name = name + " Over " + str(end_age)
        curr_code = code + str(99) + affix
        comps.append(Competition(end_age+1, 99, curr_name, curr_code, "All", code))
    else:
        for age in range(start_age, end_age+1, step):
            b_name = "Boys " + name + " Under " + str(age)
            b_code = "B" + code + str(age) + affix
            g_name = "Girls " + name + " Under " + str(age)
            g_code = "G" + code + str(age) + affix
            comps += [Competition(prev_age, age, b_name, b_code, "Male", code),
                      Competition(prev_age, age, g_name, g_code, "Female", code)]
            prev_age = age + 1
        b_name = "Boys " + name + " Over " + str(end_age)
        b_code = "B" + code + str(99) + affix
        g_name = "Girls " + name + " Over " + str(end_age)
        g_code = "G" + code + str(99) + affix
        comps += [Competition(end_age+1, 99, b_name, b_code, "Male", code),
                  Competition(end_age+1, 99, g_name, g_code, "Female", code)]
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
                comps.append(Competition(prev_age, age, curr_name, curr_code, "All", code))
                prev_age = age + 1
            curr_name = name + " Over " + str(end_age) + " " + dance[0]
            curr_code = code + str(99) + dance[1]
            comps.append(Competition(end_age+1, 99, curr_name, curr_code, "All", code))
        else:
            for age in range(start_age, end_age+1, step):
                b_name = "Boys " + name + " Under " + str(age) + " " + dance[0]
                b_code = "B" + code + str(age) + dance[1]
                g_name = "Girls " + name + " Under " + str(age) + " " + dance[0]
                g_code = "G" + code + str(age) + dance[1]
                comps += [Competition(prev_age, age, b_name, b_code, "Male", code),
                          Competition(prev_age, age, g_name, g_code, "Female", code)]
                prev_age = age + 1
            b_name = "Boys " + name + " Over " + str(end_age) + " " + dance[0]
            b_code = "B" + code + str(99) + dance[1]
            g_name = "Girls " + name + " Over " + str(end_age) + " " + dance[0]
            g_code = "G" + code + str(99) + dance[1]
            comps += [Competition(end_age+1, 99, b_name, b_code, "Male", code),
                      Competition(end_age+1, 99, g_name, g_code, "Female", code)]
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
    if boys is None:
        for age in range(start, age_max+1, step):
            if prev_age == 0:
                curr_name = "Under " + str(age)
            else:
                curr_name = str(prev_age) + " to " + str(age)
            curr_code = "U" + str(age)
            comps['Main'].append(Competition(prev_age, age, curr_name, curr_code, "All", "All"))
            prev_age = age + 1
        curr_name = "Over " + str(age_max)
        curr_code = "O" + str(age_max)
        comps['Main'].append(Competition(prev_age, age_max+1, curr_name, curr_code, "All", "All"))
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
        b_name = "Boys Over " + str(age_max)
        b_code = "BU" + str(age_max)
        g_name = "Girls Over " + str(age_max)
        g_code = "GU" + str(age_max)
        comps['Main'] += [Competition(prev_age, age_max+1, b_name, b_code, "Male", "All"),
                          Competition(prev_age, age_max+1, g_name, g_code, "Female", "All")]
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
        name = info['level'][i]
        if info['level'][i] != "All":
            code = info['level'][i][0]
        else:
            code = ""
        gender = info['gender'][i]
        sex = "All"
        if gender == "female":
            name += " Girls "
            code = "G" + code
            sex = "Female"
        elif gender == "male":
            name += " Boys "
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
