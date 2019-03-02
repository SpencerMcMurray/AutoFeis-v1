import gc
from werkzeug.security import generate_password_hash
from database import Database


def create_sheet(comp):
    """(int) -> int
    Creates a sheet with the given comp id, and returns the created id
    """
    db = Database()
    db.cur.execute("""INSERT INTO `sheet` (`judge`) VALUES (%s)""", comp)
    sheet_id = db.cur.lastrowid
    db.con.close()
    gc.collect()
    return sheet_id


def get_judge_from_id(judge_id):
    """(int) -> dict of str:obj
    Returns the judge with the given id
    """
    db = Database()
    db.cur.execute("""SELECT * FROM `judge` WHERE `id` = %s""", judge_id)
    judge = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return judge


def delete_sheet(sheet):
    """(int) -> NoneType
    Deletes the sheet with given id
    """
    db = Database()
    db.cur.execute("""DELETE FROM `sheet` WHERE `id` = %s""", sheet)
    db.con.close()
    gc.collect()


def get_sheets_from_comp(comp):
    """(int) -> list of dict of str:int/str
    Returns the list of all sheets and their judge
    """
    db = Database()
    q = """SELECT * FROM `judge` WHERE `comp` = %s"""
    db.cur.execute(q, comp)
    formatted_sheets = list()
    judges = db.cur.fetchall()
    q = """SELECT * FROM `sheet` WHERE `judge` = %s"""
    for judge in judges:
        db.cur.execute(q, judge['id'])
        sheets = db.cur.fetchall()
        for sheet in sheets:
            formatted_sheets.append({'judge': judge['name'], 'id': sheet['id']})
    db.con.close()
    gc.collect()
    return formatted_sheets


def create_judges(judges, comp):
    """(list of str, int) -> NoneType
    Creates len(judges) judges with the names contained in the given list
    """
    db = Database()
    for judge in judges:
        db.cur.execute("""INSERT INTO `judge` (`name`, `comp`) VALUES (%s, %s)""", (judge, comp))
    db.con.close()
    gc.collect()


def delete_judge(judge_id):
    """(int) -> NoneType
    Deletes everything attached to the given judge
    """
    db = Database()
    db.cur.execute("""DELETE FROM `judge` WHERE `id` = %s""", judge_id)
    db.cur.execute("""SELECT `id` FROM `sheet` WHERE `judge` = %s""", judge_id)
    sheets = db.cur.fetchall()
    for sheet in sheets:
        db.cur.execute("""DELETE FROM `mark` WHERE `sheet` = %s""", sheet['id'])
    db.cur.execute("""DELETE FROM `sheet` where `judge` = %s""", judge_id)
    db.con.close()
    gc.collect()


def get_judges_from_comp(comp_id):
    """(int) -> list of dict of str:obj
    Returns the list of judges to the given competition
    """
    db = Database()
    q = """SELECT * FROM `judge` WHERE `comp` = %s"""
    db.cur.execute(q, comp_id)
    judges = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return judges


def delete_comp(comp_id):
    """(int) -> NoneType
    Deletes the competition with the given id
    """
    db = Database()
    q = """DELETE FROM `competition` WHERE `id` = %s"""
    db.cur.execute(q, comp_id)
    db.con.close()
    gc.collect()


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
    is_open = db.cur.fetchone()['isOpen']
    db.con.close()
    gc.collect()
    return bool(is_open)


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


def get_comps_from_feis_id(feis_id):
    """(int) -> list of dict of str:obj
    Gets all competitions associated with the given feis id
    """
    db = Database()
    q = """SELECT * FROM `competition` WHERE `feis` = %s ORDER BY `dance`, `level`, `minAge`"""
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


def update_feis(feis_id, name, date, location, region, website):
    """(int, str, stt, str, str, str) -> NoneType
    Updates the old feis info of feis with id given to be the info given
    """
    db = Database()
    q = """UPDATE `feiseanna` SET `name` = %s, `date` = %s, `location` = %s, `region` = %s, `website` = %s WHERE
           `id` = %s"""
    db.cur.execute(q, (name, date, location, region, website, feis_id))
    db.con.close()
    gc.collect()


def create_comps(feis_id, comps):
    """(int, dict of str:list of Competition) -> NoneType
    Inserts all the Competitions given by comps to the Database, under the feis with id given
    """
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


def create_feis(forg, name, date, location, region, website):
    """(int, str, str, str, str, str) -> int
    Returns the id of the feis that is created in this function with the given inputs
    """
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


def get_dancer_from_id(dancer_id):
    """(int) -> sict of str:obj
    Returns the dancer with the given id
    """
    db = Database()
    q = "SELECT * FROM `dancer` WHERE `id` = %s"
    db.cur.execute(q, dancer_id)
    dancer = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return dancer


def delete_dancer_from_id(uid):
    """(int) -> NoneType
    Deletes the dancer with the given id
    """
    db = Database()
    q = "DELETE FROM `dancer` WHERE `id` = %s"
    db.cur.execute(q, (uid,))
    db.con.close()
    gc.collect()


def update_dancer(dancer_id, f_name, l_name, school, birth_year, level, gender, show):
    """(int, str, str, str, int, str, str, int) -> NoneType
    Updates the dancer with dancer_id to have the given info
    """
    db = Database()
    q = """UPDATE `dancer` SET `fName` = %s, `lName` = %s, `birthYear` = %s, `school` = %s, `level` = %s,
    `gender` = %s, `show` = %s WHERE `id` = %s"""
    db.cur.execute(q, (f_name, l_name,  birth_year, school, level, gender, show, dancer_id))
    db.con.close()
    gc.collect()


def create_dancer(user_id, f_name, l_name, school, birth_year, level, gender, show):
    """(int, str, str, str, int, str, str, int) -> NoneType
    Creates a dancer for the user with user_id to have the given info
    """
    db = Database()
    q = """INSERT INTO `dancer` (`user`, `fName`, `lName`, `birthYear`, `school`, `level`, `gender`, `show`) VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s)"""
    db.cur.execute(q, (user_id, f_name, l_name, birth_year, school, level, gender, show))
    db.con.close()
    gc.collect()


def get_feiseanna_with_forg(forg_id):
    """(int) -> list of dict of str:obj
    Returns all feiseanna owned by the organizer with the given id
    """
    db = Database()
    db.cur.execute("SELECT * FROM `feiseanna` WHERE `forg` = %s ORDER BY `date` ASC", forg_id)
    res = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return res


def get_feis_with_id(feis_id):
    """(int) -> dict of str:obj
    Returns the feiseanna with the given id
    """
    db = Database()
    db.cur.execute("""SELECT * FROM `feiseanna` WHERE `id` = %s""", feis_id)
    res = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return res


def get_dancers_with_user(user_id):
    """(int) -> list of dict of str:obj
    Returns all dancers made by the user with the given id
    """
    db = Database()
    db.cur.execute("SELECT * FROM `dancer` WHERE `user` = %s", user_id)
    res = db.cur.fetchall()
    db.con.close()
    gc.collect()
    return res


def get_id_from_email(email):
    """(str) -> int
    Returns the id of the user with the given email
    """
    db = Database()
    num_rows = db.cur.execute("SELECT `id` FROM `users` WHERE `email` = %s", email)
    if num_rows > 0:
        return db.cur.fetchone()['id']
    db.con.close()
    gc.collect()
    return -1


def get_name_from_email(email):
    """(str) -> str
    Returns the user's name who belongs to the given email
    """
    db = Database()
    q = "SELECT `name` FROM `users` WHERE `email` = %s"
    num_rows = db.cur.execute(q, email)
    if num_rows == 0:
        return ""
    res = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return res['name']


def email_taken(email):
    """(str) -> bool
    Returns True iff the email given exists in the database
    """
    db = Database()
    q = "SELECT `email` FROM `users` WHERE `email` = %s"
    num_rows = db.cur.execute(q, (email,))
    db.con.close()
    gc.collect()
    return num_rows != 0


def sign_up(email, password, f_name, l_name):
    """(str, str, str, str) -> NoneType
    Registers the user with the given data into our Database
    """
    q = "INSERT INTO `users` (`email`, `password`, `name`) VALUES (%s, %s, %s)"
    db = Database()
    name = f_name + " " + l_name
    db.cur.execute(q, (email, generate_password_hash(password), name))
    db.con.close()
    gc.collect()


def feis_name_from_id(feis_id):
    """(int) -> str
    Returns the name of the feis with the given id
    """
    return get_feis_with_id(feis_id)['name']


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
