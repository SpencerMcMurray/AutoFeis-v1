from database import Database
from functions.databaseOps import get_judges_from_comp, get_sheets_from_judge
from functools import total_ordering
import gc
import re


# Place to irish point conversion; past 50th is 0 points
place_to_irish = {1: 100, 2: 75, 3: 65, 4: 60, 5: 56, 6: 53, 7: 50, 8: 47, 9: 45, 10: 43, 11: 40, 12: 39, 13: 38,
                  14: 37, 15: 36, 16: 35, 17: 34, 18: 33, 19: 32, 20: 31, 21: 30, 22: 29, 23: 28, 24: 27, 25: 26,
                  26: 25, 27: 24, 28: 23, 29: 22, 30: 21, 31: 20, 32: 19, 33: 18, 34: 17, 35: 16, 36: 15, 37: 14,
                  38: 13, 39: 12, 40: 11, 41: 10, 42: 9, 43: 8, 44: 7, 45: 6, 46: 5, 47: 4, 48: 3, 49: 2, 50: 1}


@total_ordering
class Dancer:
    """Manages a dancer's data"""
    def __init__(self, data):
        self.number = int(data[0])
        self.raw_scores = data[1:]
        self.total_raw = round(sum(self.raw_scores), 3)
        self.grid = 0

    def __repr__(self):
        return "#:" + str(self.number) + "\n" + "Raw Scores:" + str(self.raw_scores) + "\n" +\
               "Total Raw:" + str(self.total_raw) + "\n" + "Grid:" + str(self.grid) + "\n"

    def __lt__(self, other):
        return self.total_raw < other.total_raw

    def __eq__(self, other):
        return self.total_raw == other.total_raw


def tabulate_comp(comp):
    """(int) -> NoneType
    Creates a pdf with all tabulated mark data that one could want for the given competition
    TODO: Add some error checking(dancer numbers not matching/in db, etc.)
    """
    marks = dict()
    judges = get_judges_from_comp(comp)
    for judge in judges:
        sheets = get_sheets_from_judge(judge['id'])
        marks[judge['id']] = list()
        for sheet in sheets:
            sheet_marks = make_marks_from_sheet(sheet['id'])
            for mark in sheet_marks:
                marks[judge['id']].append(Dancer([float(f) for f in mark]))
        marks[judge['id']].sort(reverse=True)
        marks[judge['id']] = fill_grid_pts(marks[judge['id']])


def fill_grid_pts(dancers):
    """(list of Dancer) -> list of Dancer
    Calculates and fills in the correct grid points for all dancers
    REQ: dancers is sorted by each Dancer's total_raw
    """
    i = 0
    while i < len(dancers):
        ties = 0
        # As long as there is a next dancer, make sure their score isn't the same as the current one.
        while i + ties + 1 < len(dancers) and dancers[i].total_raw == dancers[i + ties + 1].total_raw:
            ties += 1
        irish_pts = get_irish_points(i + 1, ties)
        for j in range(i, i + ties + 1):
            dancers[j].grid = irish_pts
        i += ties + 1
    return dancers


def get_irish_points(place, num_ties=0):
    """(int, int) -> int or float
    Turns a placement with the given number of ties(two people implies 1 tie) into points on the Irish CLRG grid scale.
    """
    if place > 50:
        pts = 0
    elif num_ties > 0:
        pts = get_tie(place, num_ties)
    else:
        pts = place_to_irish[place]
    return round(pts, 2)


def get_tie(start_place, num_ties):
    """(int, int) -> int or float
    Returns the number of Irish points that should be given to a dancer at start_place when there are num_ties ties.
    """
    total = 0
    for i in range(start_place, num_ties + start_place + 1):
        total += place_to_irish[i]
    return total/(num_ties + 1)


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
    q = """SELECT `data` FROM `mark` WHERE `sheet` = %s"""
    db.cur.execute(q, sheet)
    marks = db.cur.fetchall()
    for i in range(len(marks)):
        marks[i] = marks[i]['data'].split(',')
    db.con.close()
    gc.collect()
    return marks
