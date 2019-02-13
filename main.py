import os

from flask import Flask, render_template, request, redirect, url_for, session
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

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = "static/storage/syllabi"
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024     # 10MB Upload limit

login_manager = LoginManager()
login_manager.init_app(app)

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
                                      app.config['MAX_CONTENT_LENGTH'])
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
    # TODO: Add current info as default input values
    if request.method != "POST":
        return redirect(url_for('welcome'))
    dancer = db.get_dancer_from_id(request.form.get('dancerId', 0))
    form = dcr.set_defaults_for_dancer(dancer, CreateDancer(request.form))
    return render_template("createDancer/editDancer.html", is_logged=current_user.is_authenticated, where="welcome",
                           form=form, id=dancer['id'])


@app.route("/welcome/edit_dancer/alter", methods=["POST"])
@login_required
def alter_dancer():
    """The path through altering a dancer"""
    if request.method != "POST":
        return redirect(url_for('welcome'))
    db.update_dancer(request.form.get('id', -1), request.form.get('f_name', ''), request.form.get('l_name', ''),
                     request.form.get('school', ''),  request.form.get('year', -1), request.form.get('level', ''),
                     request.form.get('gender', ''), int(request.form.get('show', -1)))
    return redirect(url_for('welcome'))


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
        if 'go' in session:
            session.pop('go')

            # Update feis
            db.update_feis(feis_id, request.form.get('name'), request.form.get('date'), request.form.get('location'),
                           request.form.get('region'), request.form.get('website'))

            # Upload new syllabus if entered
            if 'syllabus' in request.files:
                file = request.files['syllabus']
                cf.upload_file(file, feis_id, app.config["UPLOAD_FOLDER"])
            return redirect(url_for('welcome'))
        session['go'] = True
        feis = db.get_feis_with_id(feis_id)
        form = cf.set_defaults_for_feis(feis, FeisInfoForm(request.form))
        return render_template("functions/editFeisInfo.html", is_logged=current_user.is_authenticated, where="welcome",
                               feis=feis, form=form)
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


@app.route("/welcome/organize/choose", methods=["POST"])
@login_required
def choose_comp_type():
    """The page displaying the competition types to show
    TODO: Merge with show_comps, that'd be cool"""
    if request.method == "POST":
        comp_types = ["Main", "Treble Reel", "Figure", "Art", "Special"]
        return render_template("functions/pickCompType.html", is_logged=current_user.is_authenticated, where="welcome",
                               comp_types=comp_types, feis_id=request.form.get('feisId', 0))
    return redirect(url_for("welcome"))


@app.route("/welcome/organize/choose/show", methods=["POST"])
@login_required
def show_comps():
    """The Page displaying all competitions of the given type"""
    if request.method == "POST":
        feis_id, comp_type = request.form.get('feisId'), request.form.get('type')
        titles, tables = fops.make_titles_tables_for(feis_id, comp_type)
        return render_template("functions/showCompType.html", is_logged=current_user.is_authenticated, where="welcome",
                               titles=titles, tables=tables)
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
