import csv
import os

from werkzeug.utils import secure_filename


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


def make_comp_from_data(data):
    """(list of obj) -> Competition
    Returns a competition with the given data; used with serialization
    """
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


def upload_file(file, name, upload_folder):
    """(File, str, str) -> NoneType
    Uploads the given file, with the given filename, into the given folder
    """
    filename = str(name) + ".pdf"
    if file and allowed_file(filename):
        file.save(os.path.join(upload_folder, secure_filename(filename)))


def get_regions():
    """() -> list of tuple of str
    Reads a csv with all the regions, and returns them as a formatted list to be put in a select input
    """
    with open("static/csv/regions.csv", 'r') as my_file:
        reader = csv.reader(my_file, delimiter='\t')
        regions = list()
        for row in list(reader):
            regions.append((row[0], row[0]))
        return regions


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


def allowed_file(filename):
    """(str) -> bool
    Returns True iff the filename is an allowed file
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'


def make_champ_comps(start_age, end_age, step, name, code, affix, boys):
    """(int, int, int, str, str, str, bool) -> list of Competition
    Returns the list of all Championship competitions built with the given inputs
    """
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
    """(int, int, int, str, str, bool, list of list of str) -> list of Competition
    Returns the list of all Grades competitions built with the given inputs
    """
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


def make_main_competitions(single_ages, boys_champ, boys_grades, champ_max, prelim_max, set_max, grades_max):
    """(bool, bool, bool, int, int, int, int) -> dict of str:list of Competition
    Returns the formatted dict of level-name to list of competitions for that level defined by the given input
    """
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
    """(bool, bool, int) -> dict of str:list of Competition
    Returns the formatted dict of Main to the list of all main competitions defined by the given input
    """
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
    """(dict of str:obj) -> dict of str:list of Competition
    Returns the formatted dict containing all the Figure Competitions defined by info
    """
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
    """(dict of str:obj) -> dict of str:list of Competition
    Returns the formatted dict containing all the Treble Reel Competitions defined by info
    """
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
    """(dict of str:obj) -> dict of str:list of Competition
    Returns the formatted dict containing all the Tir na nOg Competitions defined by info
    """
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
    """(dict of str:obj) -> dict of str:list of Competition
    Returns the formatted dict containing all the Art Competitions defined by info
    """
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
    """(dict of str:obj) -> dict of str:list of Competition
    Returns the formatted dict of all the levels paired with all Competitions built with the info provided in session
    # TODO: Allow for much deeper customization
    """
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
