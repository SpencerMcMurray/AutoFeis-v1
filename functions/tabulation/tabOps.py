from database import Database
import gc


def save_marks(data, sheet):
    """(list of int, int) -> NoneType
    Creates a row in the mark table with the given data associated with the given sheet
    """
    db = Database()
    q = """INSERT INTO `mark` (`sheet`, `data`) VALUES (%s, %s)"""
    # Make comma-separated string out of data
    marks = ""
    for entry in data:
        marks += (entry + ",")
    marks = marks[:-1]
    db.cur.execute(q, (sheet, marks))
    db.con.close()
    gc.collect()


def make_marks_from_sheet(sheet):
    """(int) -> list of list of int
    Returns the formatted list of lists of marks & dancer numbers stored in this sheet
    """
    db = Database()
    q = """SELECT * FROM `mark` WHERE `sheet` = %s"""
    db.cur.execute(q, sheet)
    marks = db.cur.fetchall()
    for i in range(len(marks)):
        marks[i] = marks[i]['data'].split(',')
    db.con.close()
    gc.collect()
    return marks
