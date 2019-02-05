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
