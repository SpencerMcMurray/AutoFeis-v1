import gc
from database import Database


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
