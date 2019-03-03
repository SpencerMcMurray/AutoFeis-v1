from database import Database
import gc
import re


def fetch_ordered_rows(form):
    """(dict of str:obj) -> list of list of str
    Returns all entries sorted by row
    """
    # Used for sorting using the int within the string
    def atoi(text):
        return int(text) if text.isdigit() else text

    def natural_keys(text):
        return [atoi(c) for c in re.split(r'(\d+)', text)]

    entries = list()
    for element in form:
        if element.startswith('entries'):
            entries.append(element)
    entries.sort(key=natural_keys)
    for i in range(len(entries)):
        entries[i] = form.getlist(entries[i])
    return entries


def fetch_mark_errors(form):
    """(dict of str:obj) -> set of str
    Returns all errors with the given mark form
    """
    errors = set()
    for element in form:
        if element.startswith('entries'):
            data = form.getlist(element)
            for entry in data:
                for char in entry:
                    if char.isalpha():
                        errors.add("All entries must be numbers")
                        return errors
    return errors


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
