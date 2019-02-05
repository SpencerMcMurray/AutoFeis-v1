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
