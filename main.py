import os
from json import loads

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_user, login_required

from form import *
from functions import authenticate as auth
from functions import createDancer as dcr
from functions import createFeis as cf
from functions import databaseOps as db
from functions import entries as en
from functions import feisOps as fops
from functions import register as reg
from functions import results as res
from functions.tabulation import tabOps as tab

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = "static/storage/syllabi"
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024     # 10MB Upload limit

login_manager = LoginManager()
login_manager.init_app(app)


""" AJAX REQUESTS """


@app.route("/welcome/tabulate/judges/check", methods=["POST"])
@login_required
def check_dancer_num():
    """A script for checking if a dancer is registered under this competition"""
    data = list()
    for key in request.form.keys():
        data.append(loads(key))
    # data[0] contains dict contents
    data = {**data[0]}
    is_valid = db.check_valid_competitor(float(data['num']), int(data['comp']))
    result = {'valid': int(is_valid)}
    resp = jsonify(result)
    return resp


""" FLASK LOGIN """


@login_manager.user_loader
def load_user(user_id):
    user = db.get_user_from_id(int(user_id))
    return User(user['id'], user['email'], user['name'])


class User(UserMixin):
    def __init__(self, usr_id, email, name):
        self.id = int(usr_id)
        self.email = email
        self.name = name


@app.before_request
def make_session_permanent():
    session.permanent = True


""" HTTP ERROR HANDLING """


@app.errorhandler(404)
def catch_404(e):
    """Catching the 404 not found error"""
    return render_template("errorCatching/404.html")


@app.errorhandler(401)
def catch_401(e):
    """Catching the 401 unauthorized error"""
    return redirect(url_for('index'))


""" APP PAGES """


@app.route("/")
def index():
    """The index page"""
    feiseanna = db.get_latest_three_feiseanna()
    return render_template("index.html", is_logged=current_user.is_authenticated, where="home", feiseanna=feiseanna)


@app.route("/about")
def about():
    """The about page"""
    return render_template("about.html", is_logged=current_user.is_authenticated, where="about")


@app.route("/info")
def feisinfo():
    """The Feis info page"""
    feiseanna = db.get_all_feiseanna()
    return render_template("feisInfo.html", is_logged=current_user.is_authenticated, where="feisinfo",
                           feiseanna=feiseanna)


@app.route("/results", methods=['GET', 'POST'])
def results():
    """The results page"""
    if request.method == "POST":
        feis_id = request.form.get('id', 0)
        levels, comps = res.get_comps_by_level(feis_id)
        return render_template("results/resultsForFeis.html", is_logged=current_user.is_authenticated, where="results",
                               comps=comps)
    feiseanna = db.get_all_clopen_feiseanna(False)
    return render_template("results/results.html", is_logged=current_user.is_authenticated, where="results",
                           feiseanna=feiseanna)


@app.route("/entries/<int:feis>")
def entries(feis):
    """The entries page
    TODO: Take away id from url
    TODO: Use flex to make nicer"""
    return render_template("entries.html", is_logged=current_user.is_authenticated, where="feisinfo",
                           entries=en.get_entries_from_feis(feis),
                           name=db.feis_name_from_id(feis))


@app.route("/register", methods=["GET", "POST"])
def register_page():
    """The register page"""
    if request.method == "POST":
        if request.form.get("startScript", None) is None:
            session['feis_id'] = request.form.get("id", -1)
        # Get the feis info and all the user's dancers
        feis = db.get_feis_with_id(session['feis_id'])
        dancers = db.get_dancers_with_user(current_user.id)

        if request.form.get("startScript", None) is not None:
            for dancer in dancers:
                reg.register(request.form.getlist('register[' + str(dancer['id']) + '][]'), feis['id'], dancer['id'])
            session.pop('feis_id')
            return redirect(url_for('welcome'))

        comps = reg.get_all_comps_for_dancers(session['feis_id'], dancers)

        return render_template("registration/registerFor.html", is_logged=current_user.is_authenticated,
                               where="register", feis_name=feis['name'], dancers=dancers, comps=comps)
    feiseanna = db.get_all_clopen_feiseanna(True)
    return render_template("registration/register.html", is_logged=current_user.is_authenticated, where="register",
                           feiseanna=feiseanna)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """The sign up page"""
    errors = list()
    form = RegistrationForm(request.form)
    if request.method == "POST":

        # Create any errors needed
        errors = auth.fetch_signup_errors(form)
        if len(errors) > 0:
            return render_template("signUp.html", form=form, is_logged=current_user.is_authenticated, where="signup",
                                   errors=errors)
        # Otherwise sign the user up
        db.sign_up(form.email.data, form.password.data, form.f_name.data, form.l_name.data)
        return redirect(url_for('login'))
    return render_template("signUp.html", form=form, is_logged=current_user.is_authenticated, where="signup",
                           errors=errors)


@app.route("/login", methods=["GET", "POST"])
def login():
    """The login page"""
    # If the user is logged in, send them to the welcome page
    if current_user.is_authenticated:
        return redirect(url_for("welcome"))
    errors = list()
    form = LoginForm(request.form)
    if request.method == "POST":
        errors = auth.fetch_login_errors(form)
        if len(errors) > 0:
            return render_template("logIn.html", form=form, is_logged=current_user.is_authenticated, where="login",
                                   errors=errors)
        # Log the user in
        user = db.get_user_from_email(form.email.data)
        login_user(User(user['id'], user['email'], user['name']))
        return redirect(url_for("welcome"))
    return render_template("logIn.html", form=form, is_logged=current_user.is_authenticated, where="login",
                           errors=errors)


@app.route("/logout")
@login_required
def logout():
    """The logout page"""
    logout_user()
    return redirect(url_for("index"))


@app.route("/welcome", methods=['GET', 'POST'])
@login_required
def welcome():
    """The welcome page"""
    dancers = db.get_dancers_with_user(current_user.id)
    feiseanna = db.get_feiseanna_with_forg(current_user.id)
    return render_template("welcome.html", is_logged=current_user.is_authenticated, where="welcome", dancers=dancers,
                           feiseanna=feiseanna, name=current_user.name)


@app.route("/terms")
def terms():
    """The terms of service page"""
    # TODO: Write this up
    return render_template("tos.html", is_logged=current_user.is_authenticated, where="signup")


""" TABULATION """


@app.route("/welcome/tabulate/comps", methods=["POST"])
@login_required
def choose_tab_comp():
    """The page for choosing a competition to tabulate"""
    # TODO: Add search feature
    feis_id = request.form.get('feisId')
    if feis_id is None:
        feis_id = session['feis']
    feis = db.get_feis_with_id(feis_id)
    comps = db.get_comps_from_feis_id(feis_id)
    return render_template("tabulation/chooseComp.html", is_logged=current_user.is_authenticated, where="welcome",
                           feis=feis, comps=comps)


@app.route("/welcome/tabulate/judges/del-sheet", methods=["POST"])
@login_required
def del_sheet():
    """Script for deleting a sheet"""
    comp_id = request.form.get('compId')
    session['compId'] = comp_id
    db.delete_sheet(request.form.get('sheetId'))
    return redirect(url_for('render_judges'), code=307)


@app.route("/welcome/tabulate/judges/del-judge", methods=["POST"])
@login_required
def del_judge():
    """Script for deleting a judge"""
    comp_id = request.form.get('compId')
    session['compId'] = comp_id
    db.delete_judge(request.form.get('judgeId'))
    return redirect(url_for('render_judges', addJudges=1), code=307)


@app.route("/welcome/tabulate/judges/make", methods=["POST"])
@login_required
def make_judges():
    """Script for creating a list of judges"""
    comp_id = request.form.get('compId')
    session['compId'] = comp_id
    judges_to_add = request.form.getlist('Judge[]')
    db.create_judges(judges_to_add, comp_id)
    return redirect(url_for('render_judges'), code=307)


@app.route("/welcome/tabulate/judges", methods=["POST"])
@login_required
def render_judges():
    """Renders to define_judges if they aren't defined, otherwise to select_sheet"""
    comp_id = request.form.get('compId')
    if 'compId' in session:
        comp_id = session['compId']
    add_judges = request.form.get('addJudges')
    if add_judges is None:
        add_judges = request.args.get('addJudges')
    # Start rendering either define judges, or select sheet
    comp = db.get_comp_from_id(comp_id)
    judges = db.get_judges_from_comp(comp_id)
    if len(judges) == 0 or add_judges is not None:
        return render_template("tabulation/defineJudges.html", is_logged=current_user.is_authenticated, where="welcome",
                               judges=judges, comp=comp)
    sheets = db.get_sheets_from_comp(comp_id)
    return render_template("tabulation/selectSheet.html", is_logged=current_user.is_authenticated, where="welcome",
                           comp=comp, judges=judges, sheets=sheets)


@app.route("/welcome/tabulate/judges/marks", methods=["POST"])
@login_required
def enter_marks():
    """The page for entering marks"""
    # TODO: Add AutoAssist button
    errors = tab.fetch_mark_errors(request.form)
    marks = [['', '', '']]
    stop_loading = False
    # Save, only if there are't any errors
    if 'save' in request.form and len(errors) == 0:
        if 'sheetId' not in request.form:
            sheet_id = db.create_sheet(request.form.get('judgeId'))
        else:
            sheet_id = request.form.get('sheetId')
            db.clear_sheet(sheet_id)
        # Grab all the entries lists and save them as marks
        rows = tab.fetch_ordered_rows(request.form)
        for row in rows:
                tab.save_marks(row, sheet_id)

        comp_id = request.form.get('compId')
        session['compId'] = comp_id
        return redirect(url_for('render_judges'), code=307)
    # Otherwise make sure previous rows still reappear even though not saved
    elif 'save' in request.form:
        stop_loading = True
        marks = tab.fetch_ordered_rows(request.form)

    sheet_id = -1
    if 'sheetId' in request.form:
        sheet_id = request.form.get('sheetId')
        if not stop_loading:
            marks = tab.make_marks_from_sheet(sheet_id)
    judge = db.get_judge_from_id(request.form.get('judgeId'))
    return render_template("tabulation/enterMarks.html", is_logged=current_user.is_authenticated, where="welcome",
                           marks=marks, judge=judge, sheet=sheet_id, errors=errors)


@app.route("/welcome/tabulate/judges/tabulate", methods=["POST"])
@login_required
def tabulate_marks():
    """The tabulation script"""
    comp_id = request.form.get('compId')
    tab.tabulate_comp(comp_id)
    db.indicate_tabulated_comp(comp_id)
    session['feis'] = db.get_feis_id_with_comp(comp_id)
    return redirect(url_for('choose_tab_comp'), code=307)


""" ADD FEIS """


@app.route("/welcome/add_feis/start")
@login_required
def start_add_feis():
    """Add feis: defining traits page"""
    traits = ChooseTraitsForm(request.form)
    return render_template("createFeis/addFeisStart.html", is_logged=current_user.is_authenticated, where='welcome',
                           form=traits)


@app.route("/welcome/add_feis/ages")
@login_required
def ages_add_feis():
    """Add feis: defining ages page"""
    session['single_ages'] = bool(int(request.args.get('single_ages')))
    session['levels'] = bool(int(request.args.get('levels')))
    session['boys_champ'] = bool(int(request.args.get('separate_by_sex_champ')))
    session['boys_grades'] = bool(int(request.args.get('separate_by_sex_grades')))
    choices = dcr.age_dropdown(session.get('single_ages'))
    return render_template("createFeis/addFeisAges.html", is_logged=current_user.is_authenticated,
                           where='welcome', choices=choices, is_local=session['levels'])


@app.route("/welcome/add_feis/basic")
@login_required
def basic_add_feis():
    """Add feis: defining basic extra comps page"""
    if session.get('levels'):
        session['champ_max'] = int(request.args.get('champ'))
        session['prelim_max'] = int(request.args.get('prelim'))
        session['set_max'] = int(request.args.get('sets'))
        session['grades_max'] = int(request.args.get('grades'))
    else:
        session['main_max'] = int(request.args.get('main'))
    return render_template("createFeis/addFeisBasic.html", is_logged=current_user.is_authenticated,
                           where='welcome')


@app.route("/welcome/add_feis/art")
@login_required
def art_add_feis():
    """Add feis: defining extra special comps page"""
    figures = dict()
    figures['type'] = request.args.getlist('FGType[]')
    figures['start_age'] = request.args.getlist('FGStartAge[]')
    figures['end_age'] = request.args.getlist('FGEndAge[]')
    figures['gender'] = request.args.getlist('FGGender[]')

    # Setup TR info
    treble = dict()
    treble['start_age'] = request.args.getlist('TRStartAge[]')
    treble['end_age'] = request.args.getlist('TREndAge[]')
    treble['gender'] = request.args.getlist('TRGender[]')
    treble['level'] = request.args.getlist('TRLevel[]')

    # Setup TNN info
    tir = dict()
    tir['start_age'] = request.args.getlist('TNNStartAge[]')
    tir['end_age'] = request.args.getlist('TNNEndAge[]')

    session['FG_info'] = figures
    session['TR_info'] = treble
    session['TNN_info'] = tir
    return render_template("createFeis/addFeisArt.html", is_logged=current_user.is_authenticated,
                           where='welcome')


@app.route("/welcome/add_feis/unique")
@login_required
def unique_add_feis():
    """Add feis: defining unique comps page"""
    art = dict()
    art['start_age'] = request.args.getlist('ARStartAge[]')
    art['end_age'] = request.args.getlist('AREndAge[]')
    art['gender'] = request.args.getlist('ARGender[]')
    art['name'] = request.args.getlist('ARName[]')

    session['AR_info'] = art
    return render_template("createFeis/addFeisUnique.html", is_logged=current_user.is_authenticated,
                           where='welcome')


@app.route("/welcome/add_feis/show")
@login_required
def show_add_feis():
    """Add feis: Show all comps page"""
    # TODO: Make look a bit cleaner
    special = dict()
    special['start_age'] = request.args.getlist('SPStartAge[]')
    special['end_age'] = request.args.getlist('SPEndAge[]')
    special['gender'] = request.args.getlist('SPGender[]')
    special['name'] = request.args.getlist('SPName[]')
    special['level'] = request.args.getlist('SPLevel[]')

    session['SP_info'] = special

    # Create comps from data
    comps = cf.get_comps_from_session(session)

    session['comps'] = cf.serialize_comps(comps)

    return render_template("createFeis/addFeisShow.html", is_logged=current_user.is_authenticated,
                           where='welcome', comps=comps)


@app.route("/welcome/add_feis/info", methods=["GET", "POST"])
@login_required
def info_add_feis():
    """Add feis: defining feis details page"""
    info_form = FeisInfoForm(request.form)
    errors = list()
    if request.method == "POST":
        print(request.files['syllabus'].content_type)
        errors = cf.fetch_feis_errors(info_form, request.form.get('date'), request.files.get('syllabus', None),
                                      app.config['MAX_CONTENT_LENGTH'], False)
        if len(errors) > 0:
            return render_template("createFeis/addFeisInfo.html", is_logged=current_user.is_authenticated,
                                   where='welcome', form=info_form, errors=errors)

        # TODO: Include pay-wall here
        # Create feis
        feis_id = db.create_feis(current_user.id, request.form.get('name'),
                                 request.form.get('date'), request.form.get('location'), request.form.get('region'),
                                 request.form.get('website'))

        # Upload file
        file = request.files['syllabus']
        cf.upload_file(file, feis_id, app.config["UPLOAD_FOLDER"])

        # Create all competitions
        db.create_comps(feis_id, cf.deserialize_comps(session['comps']))

        # Get rid of unneeded session vars
        session.pop('comps')
        session.pop('FG_info')
        session.pop('TR_info')
        session.pop('TNN_info')
        session.pop('AR_info')
        session.pop('SP_info')
        if session.get('levels'):
            session.pop('champ_max')
            session.pop('prelim_max')
            session.pop('set_max')
            session.pop('grades_max')
        else:
            session.pop('main_max')
        return redirect(url_for('welcome'))

    return render_template("createFeis/addFeisInfo.html", is_logged=current_user.is_authenticated,
                           where='welcome', form=info_form, errors=errors)


@app.route("/welcome/add_dancer", methods=['GET', 'POST'])
@login_required
def add_dancer():
    """The add dancer page"""
    form = CreateDancer(request.form)
    errors = list()
    if request.method == "POST":
        errors = dcr.fetch_dancer_errors(form)
        if len(errors) > 0:
            return render_template("createDancer/addDancer.html", is_logged=current_user.is_authenticated,
                                   where="welcome", form=form, errors=errors)
        db.create_dancer(current_user.id, form.f_name.data, form.l_name.data, form.school.data, int(form.year.data),
                         form.level.data, form.gender.data, int(form.show.data))
        return redirect(url_for("welcome"))
    return render_template("createDancer/addDancer.html", is_logged=current_user.is_authenticated, where="welcome",
                           form=form, errors=errors)


@app.route("/welcome/delete_dancer", methods=['POST'])
@login_required
def delete_dancer():
    """The path through deleting a dancer"""
    if request.method == "POST":
        db.delete_dancer_from_id(request.form.get('id', 0))
    return redirect(url_for('welcome'))


@app.route("/welcome/edit_dancer", methods=['POST'])
@login_required
def edit_dancer():
    """The edit dancer page for a given dancer"""
    if request.method != "POST":
        return redirect(url_for('welcome'))
    form = CreateDancer(request.form)
    errors = list()
    # If we have submitted an update, error check and update
    if 'id' in request.form:
        errors = dcr.fetch_dancer_errors(form)
        if len(errors) > 0:
            return render_template("createDancer/editDancer.html", is_logged=current_user.is_authenticated,
                                   where="welcome", form=form, id=request.form.get('id', -1), errors=errors,
                                   name=request.form.get('name', ''))
        db.update_dancer(request.form.get('id', -1), request.form.get('f_name', ''), request.form.get('l_name', ''),
                         request.form.get('school', ''),  request.form.get('year', -1), request.form.get('level', ''),
                         request.form.get('gender', ''), int(request.form.get('show', -1)))
        return redirect(url_for('welcome'))
    dancer = db.get_dancer_from_id(request.form.get('dancerId', 0))
    form = dcr.set_defaults_for_dancer(dancer, form)
    return render_template("createDancer/editDancer.html", is_logged=current_user.is_authenticated, where="welcome",
                           form=form, id=dancer['id'], errors=errors, name=dancer['fName'])


@app.route("/welcome/organize", methods=['POST'])
@login_required
def feis_functions():
    """The feis functions for a given feis"""
    if request.method == "POST":
        feis_id = request.form.get('feisId', 0)
        name = db.feis_name_from_id(feis_id)
        is_open = db.get_open_from_id(feis_id)
        return render_template("functions/feisFunctions.html", is_logged=current_user.is_authenticated,
                               where="welcome", name=name, is_open=is_open, feis_id=feis_id)
    return redirect(url_for('welcome'))


@app.route("/welcome/organize/edit", methods=['POST'])
@login_required
def edit_feis():
    """The edit feis function page"""
    if request.method == 'POST':
        feis_id = request.form.get('feisId', 0)
        feis = db.get_feis_with_id(feis_id)
        form = FeisInfoForm(request.form)
        errors = list()
        if 'name' in request.form:
            errors = cf.fetch_feis_errors(form, request.form.get('date'), request.files.get('syllabus', None),
                                          app.config['MAX_CONTENT_LENGTH'], True)
            if len(errors) > 0:
                return render_template("functions/editFeisInfo.html", is_logged=current_user.is_authenticated,
                                       where="welcome", feis=feis, form=form, errors=errors)
            # Update feis
            db.update_feis(feis_id, request.form.get('name'), request.form.get('date'), request.form.get('location'),
                           request.form.get('region'), request.form.get('website'))

            # Upload new syllabus if entered
            if 'syllabus' in request.files:
                file = request.files['syllabus']
                cf.upload_file(file, feis_id, app.config["UPLOAD_FOLDER"])
            return redirect(url_for('welcome'))
        form = cf.set_defaults_for_feis(feis, form)
        return render_template("functions/editFeisInfo.html", is_logged=current_user.is_authenticated, where="welcome",
                               feis=feis, form=form, errors=errors)
    return redirect(url_for("welcome"))


@app.route("/welcome/organize/alter", methods=["POST"])
@login_required
def alter_comps():
    """Page displaying all competitions, offering the split/merge ability"""
    if request.method == "POST":
        comps = db.get_comps_from_feis_id(request.form.get('feisId', 0))
        return render_template("functions/alterComps.html", is_logged=current_user.is_authenticated, where="welcome",
                               comps=comps)
    return redirect(url_for("welcome"))


@app.route("/welcome/organize/alter/merge", methods=["POST"])
@login_required
def merge():
    """Page for merging two competitions"""
    if request.method == "POST":
        if request.form.get('compatCompId', None) is not None:
            fops.merge_comps(request.form.get('compId'), request.form.get('compatCompId'))
        else:
            comp = db.get_comp_from_id(request.form.get('compId', 0))
            mergable = fops.get_mergeable_comps(comp)
            return render_template("functions/mergeComps.html", is_logged=current_user.is_authenticated,
                                   where="welcome", comp=comp, merge=mergable)
    return redirect(url_for("welcome"))


@app.route("/welcome/organize/alter/split", methods=["POST"])
@login_required
def split():
    """Page for splitting a competition in two"""
    if request.method == "POST":
        comp = db.get_comp_from_id(request.form.get('compId', 0))
        ages = [x + 1 for x in range(comp['minAge'], comp['maxAge'])]
        return render_template("functions/splitComps.html", is_logged=current_user.is_authenticated, where="welcome",
                               comp=comp, ages=ages)
    return redirect(url_for("welcome"))


@app.route("/welcome/organize/alter/split/AB", methods=["POST"])
@login_required
def split_ab():
    """Script to split one competition with one age group into two sub-comps"""
    if request.method == "POST":
        comp_id = request.form.get('compId', 0)
        comp = db.get_comp_from_id(comp_id)
        fops.split_into_ab(comp)
    return redirect(url_for("welcome"))


@app.route("/welcome/organize/alter/split/age", methods=["POST"])
@login_required
def split_age():
    """Script to split one competition with many age groups into two sub-comps"""
    if request.method == "POST":
        comp_id = request.form.get('compId', 0)
        age = int(request.form.get('age', -1))
        comp = db.get_comp_from_id(comp_id)
        fops.split_by_age(comp, age)
    return redirect(url_for("welcome"))


@app.route("/welcome/organize/show", methods=["POST"])
@login_required
def show_comps():
    """The Page displaying all competitions of the given type"""
    # TODO: Make look a bit cleaner
    if request.method == "POST":
        feis_id = request.form.get('feisId')
        name = db.get_feis_with_id(feis_id)['name']
        comps = fops.get_formatted_competitions(feis_id)
        return render_template("functions/showComps.html", is_logged=current_user.is_authenticated, where="welcome",
                               comps=comps, name=name)
    return redirect(url_for("welcome"))


@app.route("/welcome/organize/scoresheet", methods=["POST"])
@login_required
def score_calc():
    """The Scoresheet calculator page"""
    if request.method == "POST":
        feis_id = request.form.get('feisId', 0)
        comps = db.get_comps_from_feis_id(feis_id)
        sheets, total = fops.get_sheets_for_comps(comps)
        return render_template("functions/scoresheetCalc.html", is_logged=current_user.is_authenticated,
                               where="welcome", sheets=sheets, total=total)
    return redirect("welcome")
