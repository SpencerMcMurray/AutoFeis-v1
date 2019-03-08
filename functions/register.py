import gc
import datetime as dt
from database import Database


def register(reg, feis_id, dancer_id):
    """(dict of str:dict of str:int, int, int) -> NoneType
    Registers all dancer ids to the given competition id
    """
    db = Database()
    db.cur.execute("""SELECT `dancerNum` FROM `feiseanna` WHERE `id` = %s""", feis_id)
    curr_num = db.cur.fetchone()['dancerNum']
    q = """INSERT INTO `competitor` (`dancerId`, `competition`, `feis`, `number`) VALUES (%s, %s, %s, %s)"""
    for comp in reg:
        db.cur.execute(q, (dancer_id, comp, feis_id, curr_num))
    db.cur.execute("""UPDATE `feiseanna` SET `dancerNum` = `dancerNum` + 1 WHERE `id` = %s""", feis_id)
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
