from database import Database
import gc


def make_marks_from_sheet(sheet):
    """(int) -> list of list of int
    Returns the formatted list of lists of marks & dancer numbers stored in this sheet
    """
    db = Database()
    q = """SELECT * FROM `mark` WHERE `sheet` = %s"""
    db.cur.execute(q, sheet)
    marks = db.cur.fetchall()
    for i in range(len(marks)):
        marks[i] = marks[i]['marks'].split(',')
    db.con.close()
    gc.collect()
    return marks
