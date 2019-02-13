import datetime as dt
import csv


def set_defaults_for_dancer(dancer, form):
    """(dict of str:obj, Form) -> Form
    Sets all the defaults values from the dancer to the form, and returns resultant form
    """
    form.f_name.default = dancer['fName']
    form.l_name.default = dancer['lName']
    form.gender.default = dancer['gender']
    form.year.default = dancer['birthYear']
    form.school.default = dancer['school']
    form.level.default = dancer['level']
    form.show.default = dancer['show']
    form.process()
    return form


def fetch_dancer_errors(form):
    """(Form) -> list of str
    Returns a list of all errors that can be said about the given form
    """
    errors = list()
    if len(form.f_name.data) <= 0 or len(form.l_name.data) <= 0:
        errors.append("Name field(s) left blank")
    if len(form.f_name.data) >= 100 or len(form.l_name.data) >= 100:
        errors.append("Name field(s) too long")
    return errors


def age_dropdown(is_single):
    choices = list()
    offset = (1 if is_single else 2)
    for i in range(3, 100, offset):
        choices.append(str(i))
    return choices


def school_dropdown():
    with open("static/csv/schools.csv", 'r') as my_file:
        reader = csv.reader(my_file, delimiter='\t')
        regions = list()
        for row in list(reader):
            regions.append((row[0], row[0]))
        return regions


def year_dropdown():
    curr_year = dt.datetime.now().year
    choices = list()
    for i in range(curr_year, curr_year-100-1, -1):
        choices.append((str(i), str(i)))
    return choices
