from database import Database
from functions.databaseOps import get_judges_from_comp, get_sheets_from_judge, get_competitors_with_comp
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
    """Manages a dancer's data from all judges"""
    def __init__(self, num, marks):
        self.number = int(num)
        self.scores = marks
        self.total_grid = 0
        self.place = 0

    def __repr__(self):
        return "#: " + str(self.number) + "\n" + "Scores: " + str(self.scores) + "\n" + "Total Grid: " +\
               str(self.total_grid) + "\n"

    def __lt__(self, other):
        return self.total_grid < other.total_grid

    def __eq__(self, other):
        return self.total_grid == other.total_grid

    def update_grid(self, new_grid, judge):
        self.scores[judge]['grid'] = new_grid


def find_mark(sheet, num):
    """(int, int) -> dict of str:obj
    Returns the mark in the sheet for the dancer with the given number
    """
    db = Database()
    db.cur.execute("""SELECT * FROM `mark` WHERE `sheet` = %s AND `data` LIKE %s""", (sheet, str(num) + "%"))
    mark = db.cur.fetchone()
    db.con.close()
    gc.collect()
    return mark


def tabulate_comp(comp):
    """(int) -> NoneType
    Creates a pdf with all tabulated mark data that one could want for the given competition
    TODO: Currently uses cptr id as dancer number; change that
    """
    competitors = get_competitors_with_comp(comp)
    judges = get_judges_from_comp(comp)
    sheets = dict()
    # Get all sheets, and organize them by their judge
    for judge in judges:
        sheets[judge['id']] = get_sheets_from_judge(judge['id'])
    dancers = list()
    for cptr in competitors:
        marks = dict()
        for judge_id in sheets.keys():
            mark = []
            # In each sheet every dancer has at most 1 mark in it, once we find one, break
            for sheet in sheets[judge_id]:
                mark = find_mark(sheet['id'], cptr['id'])
                if mark is not None:
                    mark = mark['data'].split(',')[1:]
                    mark = [float(f) for f in mark]
                    break
            total = round(sum(mark), 3)
            marks[judge_id] = {'raw': mark, 'total': total}
        dancers.append(Dancer(cptr['id'], marks))
    dancers = fill_grid_pts(dancers)
    dancers.sort(reverse=True)
    dancers = fill_placements(dancers)


def fill_placements(dancers):
    """(list of Dancer) -> list of Dancer
    Fills in the dancer's placements including the appropriate ties
    """
    place = 1
    i = 0
    while i < len(dancers):
        ties = 0
        while i + ties < len(dancers) and dancers[i].total_grid == dancers[i + ties].total_grid:
            dancers[i + ties].place = place
            ties += 1
        place += ties
        i += ties + 1
    return dancers


def fill_grid_pts(dancers):
    """(list of Dancer) -> list of Dancer
    Calculates and fills in the correct grid points for all dancers for all judges
    """
    for judge in dancers[0].scores.keys():
        i = 0
        while i < len(dancers):
            ties = 0
            # As long as there is a next dancer, make sure their score isn't the same as the current one.
            while (i + ties < len(dancers) and
                   dancers[i].scores[judge]['total'] == dancers[i + ties + 1].scores[judge]['total']):
                ties += 1
            irish_pts = get_irish_points(i + 1, ties)
            for j in range(i, i + ties + 1):
                dancers[j].update_grid(irish_pts, judge)
            i += ties + 1
    # Update each dancers total grid points so we can sort
    for dancer in dancers:
        total = 0
        for judge in dancer.scores:
            total += judge['grid']
        dancer.total_grid = total
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
