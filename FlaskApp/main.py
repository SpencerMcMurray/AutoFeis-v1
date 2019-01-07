from functions import *
from form import *
from flask import Flask, render_template, request, redirect, url_for, flash, session
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = "static/files/syllabi"
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024     # 10MB Upload limit
# TODO: Implement flask_login!
LOGGED = False


def flip_logged():
    """flips the value of LOGGED"""
    global LOGGED
    LOGGED = not LOGGED


@app.errorhandler(404)
def catch_404(e):
    """Page for catching the 404 not found error"""
    return render_template("errorCatching/404.html")


@app.route("/")
def index():
    """The index page"""
    feiseanna = get_latest_three_feiseanna()
    return render_template("index.html", is_logged=LOGGED, where="home", feiseanna=feiseanna)


@app.route("/about")
def about():
    """The about page"""
    return render_template("about.html", is_logged=LOGGED, where="about")


@app.route("/info")
def feisinfo():
    """The Feis info page"""
    feiseanna = get_all_feiseanna()
    return render_template("feisInfo.html", is_logged=LOGGED, where="feisinfo", feiseanna=feiseanna)


@app.route("/results", methods=['GET', 'POST'])
def results():
    """The results page"""
    if request.method == "POST":
        feis_id = request.form.get('id', 0)
        comps = get_comps_from_feis_id(feis_id)
        return render_template("results/resultsForFeis.html", is_logged=LOGGED, where="results", comps=comps)
    feiseanna = get_all_clopen_feiseanna(False)
    return render_template("results/results.html", is_logged=LOGGED, where="results", feiseanna=feiseanna)


@app.route("/entries/<int:feis>")
def entries(feis):
    """The entries page
    TODO: Take away id from url
    TODO: Use flex to make nicer"""
    return render_template("entries.html", is_logged=LOGGED, where="feisinfo", entries=get_entries_from_feis(feis),
                           name=feis_name_from_id(feis))


@app.route("/register", methods=["GET", "POST"])
def register_page():
    """The register page"""
    if request.method == "POST":
        if request.form.get("startScript", None) is None:
            session['feis_id'] = request.form.get("id", -1)
        # Get the feis info and all the user's dancers
        feis = get_feis_with_id(session['feis_id'])
        dancers = get_dancers_with_user(get_id_from_email(session['email']))

        if request.form.get("startScript", None) is not None:
            for dancer in dancers:
                register(request.form.getlist('register[' + str(dancer['id']) + '][]'), feis['id'], dancer['id'])
            session.pop('feis_id')
            return redirect(url_for('welcome'))

        comps = get_all_comps_for_dancers(session['feis_id'], dancers)

        return render_template("registration/registerFor.html", is_logged=LOGGED, where="register",
                               feis_name=feis['name'], dancers=dancers, comps=comps)
    feiseanna = get_all_clopen_feiseanna(True)
    return render_template("registration/register.html", is_logged=LOGGED, where="register", feiseanna=feiseanna)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """The sign up page"""
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():

        # Check if the email given already exists
        if email_taken(form.email.data):
            flash("The email provided already belongs to a user")
            return render_template("signUp.html", form=form, is_logged=LOGGED, where="signup")

        # Otherwise sign the user up
        sign_up(form.email.data, form.password.data, form.f_name.data, form.l_name.data)
        return redirect(url_for('login'))
    return render_template("signUp.html", form=form, is_logged=LOGGED, where="signup")


@app.route("/login", methods=["GET", "POST"])
def login():
    """The login page"""
    # If the user is logged in, send them to the welcome page
    if LOGGED:
        return redirect(url_for("welcome"))

    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():

        # Make sure the email is in the database
        if not email_taken(form.email.data):
            flash("The email provided doesn't belong to a user")
            return render_template("logIn.html", form=form, is_logged=LOGGED, where="login")
        # Make sure the password matches the email given in the database
        if not validate(form.email.data, form.password.data):
            flash("The password given doesn't match with the email provided")
            return render_template("logIn.html", form=form, is_logged=LOGGED, where="login")
        # Log the user in
        session['email'] = form.email.data
        flip_logged()
        return redirect(url_for("welcome"))
    return render_template("logIn.html", form=form, is_logged=LOGGED, where="login")


@app.route("/logout")
def logout():
    """The logout page"""
    session.pop("email")
    flip_logged()
    return redirect(url_for("index"))


@app.route("/welcome", methods=['GET', 'POST'])
def welcome():
    """The (not so welcoming) welcome page"""
    feis_fcns_form = FeisFcnsForm(request.form)
    edit_dancer_form = EditDancerForm(request.form)
    add_dancer_form = AddDancerForm(request.form)
    add_feis_form = AddFeisForm(request.form)

    user_id = get_id_from_email(session['email'])
    dancers = get_dancers_with_user(user_id)
    feiseanna = get_feiseanna_with_forg(user_id)
    if request.method == 'POST':
        if request.form.get('submit', None) == "Add a Dancer":
            return redirect(url_for("add_dancer"))

        if request.form.get('submit', None) == "Add a Feis":
            return redirect(url_for("add_feis"))
    return render_template("welcome.html", is_logged=LOGGED, where="welcome",
                           dancers=dancers,
                           feiseanna=feiseanna,
                           edit_dancer=edit_dancer_form,
                           dancer_form=add_dancer_form,
                           feis_form=add_feis_form,
                           feis_fcns_form=feis_fcns_form,
                           name=get_name_from_email(session['email']))


@app.route("/terms")
def terms():
    """The terms of service page"""
    # TODO: Write this up
    return render_template("tos.html", is_logged=LOGGED, where="signup")


@app.route("/welcome/add_feis", methods=['GET', 'POST'])
def add_feis():
    """The whole add feis area... This was always gonna be ugly"""
    traits = ChooseTraitsForm(request.form)
    if request.method == "POST":
        if request.form.get('next') == 'ages':
            # Set traits
            session['single_ages'] = request.form.get('single_ages')
            session['include_levels'] = request.form.get('include_levels')
            session['anyone_register'] = request.form.get('anyone_register')
            session['boys_champ'] = request.form.get('separate_by_sex_champ')
            session['boys_grades'] = request.form.get('separate_by_sex_grades')
            choices = age_dropdown(session.get('single_ages'))
            return render_template("createFeis/addFeisAges.html", is_logged=LOGGED, where='welcome', choices=choices,
                                   is_local=session['include_levels'])

        if request.form.get('next') == 'basic':
            # Set Ages
            if session.get('include_levels'):
                session['champ_max'] = int(request.form.get('champ'))
                session['prelim_max'] = int(request.form.get('prelim'))
                session['set_max'] = int(request.form.get('sets'))
                session['grades_max'] = int(request.form.get('grades'))
            else:
                session['main_max'] = int(request.form.get('main'))
            return render_template("createFeis/addFeisBasic.html", is_logged=LOGGED, where='welcome')

        if request.form.get('next') == 'art':
            # Setup FG info
            FG_dict = dict()
            FG_dict['type'] = request.form.getlist('FGType[]')
            FG_dict['start_age'] = request.form.getlist('FGStartAge[]')
            FG_dict['end_age'] = request.form.getlist('FGEndAge[]')
            FG_dict['gender'] = request.form.getlist('FGGender[]')

            # Setup TR info
            TR_dict = dict()
            TR_dict['start_age'] = request.form.getlist('TRStartAge[]')
            TR_dict['end_age'] = request.form.getlist('TREndAge[]')
            TR_dict['gender'] = request.form.getlist('TRGender[]')
            TR_dict['level'] = request.form.getlist('TRLevel[]')

            # Setup TNN info
            TNN_dict = dict()
            TNN_dict['start_age'] = request.form.getlist('TNNStartAge[]')
            TNN_dict['end_age'] = request.form.getlist('TNNEndAge[]')

            session['FG_info'] = FG_dict
            session['TR_info'] = TR_dict
            session['TNN_info'] = TNN_dict
            return render_template("createFeis/addFeisArt.html", is_logged=LOGGED, where='welcome')

        if request.form.get('next') == 'unique':
            # Setup AR info
            AR_dict = dict()
            AR_dict['start_age'] = request.form.getlist('ARStartAge[]')
            AR_dict['end_age'] = request.form.getlist('AREndAge[]')
            AR_dict['gender'] = request.form.getlist('ARGender[]')
            AR_dict['name'] = request.form.getlist('ARName[]')

            session['AR_info'] = AR_dict
            return render_template("createFeis/addFeisUnique.html", is_logged=LOGGED, where='welcome')

        if request.form.get('next') == 'show':
            # Setup SP info
            SP_dict = dict()
            SP_dict['start_age'] = request.form.getlist('SPStartAge[]')
            SP_dict['end_age'] = request.form.getlist('SPEndAge[]')
            SP_dict['gender'] = request.form.getlist('SPGender[]')
            SP_dict['name'] = request.form.getlist('SPName[]')
            SP_dict['level'] = request.form.getlist('SPLevel[]')

            session['SP_info'] = SP_dict

            # Create comps from data
            comps = get_comps_from_session(session)

            # Get rid of old session vars, and add our comps dict.
            session.pop('FG_info')
            session.pop('TR_info')
            session.pop('TNN_info')
            session.pop('AR_info')
            session.pop('SP_info')
            if session.get('include_levels'):
                session.pop('champ_max')
                session.pop('prelim_max')
                session.pop('set_max')
                session.pop('grades_max')
            else:
                session.pop('main_max')
            session['comps'] = serialize_comps(comps)

            return render_template("createFeis/addFeisShow.html", is_logged=LOGGED, where='welcome', comps=comps)

        if request.form.get('next') == 'info':
            # TODO: Implement file validity checks
            info_form = FeisInfoForm(request.form)
            return render_template("createFeis/addFeisInfo.html", is_logged=LOGGED, where='welcome', form=info_form)

        if request.form.get('next') == 'create':
            # TODO: Include pay-wall here

            # Create feis
            feis_id = create_feis(get_id_from_email(session['email']), request.form.get('name'),
                                    request.form.get('date'), request.form.get('location'), request.form.get('region'),
                                    request.form.get('website'))

            # Upload file
            file = request.files['syllabus']
            upload_file(file, feis_id, app.config["UPLOAD_FOLDER"])

            # Create all competitions
            create_comps(feis_id, deserialize_comps(session['comps']))
            session.pop('comps')
            return redirect(url_for('welcome'))

    return render_template("createFeis/addFeisStart.html", is_logged=LOGGED, where='welcome', form=traits)


@app.route("/welcome/add_dancer", methods=['GET', 'POST'])
def add_dancer():
    """The add dancer page"""
    form = CreateDancer(request.form)
    if request.method == "POST" and form.validate():
        create_dancer(get_id_from_email(session['email']), form.f_name.data, form.l_name.data, form.school.data,
                      int(form.year.data), form.level.data, form.gender.data, int(form.show.data))
        return redirect(url_for("welcome"))

    return render_template("createDancer/addDancer.html", is_logged=LOGGED, where="welcome", form=form)


@app.route("/welcome/delete_dancer", methods=['POST'])
def delete_dancer():
    """The path through deleting a dancer"""
    if request.method == "POST":
        delete_dancer_from_id(request.form.get('id', 0))
    return redirect(url_for('welcome'))


@app.route("/welcome/edit_dancer", methods=['POST'])
def edit_dancer():
    """The edit dancer page for a given dancer"""
    # TODO: Add current info as default input values
    if request.method != "POST":
        return redirect(url_for('welcome'))
    form = CreateDancer(request.form)
    dancer = get_dancer_from_id(request.form.get('dancerId', 0))
    return render_template("createDancer/editDancer.html", is_logged=LOGGED, where="welcome", dancer=dancer, form=form)


@app.route("/welcome/edit_dancer/alter", methods=["POST"])
def alter_dancer():
    """The path through altering a dancer
    TODO: Add defaults"""
    if request.method != "POST":
        return redirect(url_for('welcome'))
    alter_dancer(request.form.get('id', -1), request.form.get('f_name', ''), request.form.get('l_name', ''),
                 request.form.get('school', ''),  request.form.get('year', -1), request.form.get('level', ''),
                 request.form.get('gender', ''), int(request.form.get('show', -1)))
    return redirect(url_for('welcome'))


@app.route("/welcome/functions", methods=['POST'])
def feis_functions():
    """The feis functions for a given feis"""
    if request.method == "POST":
        feis_id = request.form.get('feisId', 0)
        name = feis_name_from_id(feis_id)
        is_open = get_open_from_id(feis_id)
        return render_template("functions/feisFunctions.html", is_logged=LOGGED, where="welcome", name=name,
                               is_open=is_open, feis_id=feis_id)
    return redirect(url_for('welcome'))


@app.route("/welcome/functions/edit", methods=['POST'])
def edit_feis():
    """The edit feis function page"""
    if request.method == 'POST':
        feis_id = request.form.get('feisId', 0)
        if 'go' in session:
            session.pop('go')

            # Update feis
            update_feis(feis_id, request.form.get('name'), request.form.get('date'), request.form.get('location'),
                          request.form.get('region'), request.form.get('website'))

            # Upload new syllabus if entered
            if 'syllabus' in request.files:
                file = request.files['syllabus']
                upload_file(file, feis_id, app.config["UPLOAD_FOLDER"])
            return redirect(url_for('welcome'))
        session['go'] = True
        feis = get_feis_with_id(feis_id)
        form = set_defaults_for_feis(feis, FeisInfoForm(request.form))
        return render_template("functions/editFeisInfo.html", is_logged=LOGGED, where="welcome", feis=feis, form=form)
    return redirect(url_for("welcome"))


@app.route("/welcome/functions/alter", methods=["POST"])
def alter_comps():
    """Page displaying all competitions, offering the split/merge ability"""
    if request.method == "POST":
        comps = get_comps_from_feis_id(request.form.get('feisId', 0))
        return render_template("functions/alterComps.html", is_logged=LOGGED, where="welcome", comps=comps)
    return redirect(url_for("welcome"))


@app.route("/welcome/functions/alter/merge", methods=["POST"])
def merge():
    """Page for merging two competitions"""
    if request.method == "POST":
        if request.form.get('compatCompId', None) is not None:
            merge_comps(request.form.get('compId'), request.form.get('compatCompId'))
        else:
            comp = get_comp_from_id(request.form.get('compId', 0))
            mergable = get_mergeable_comps(comp)
            return render_template("functions/mergeComps.html", is_logged=LOGGED, where="welcome", comp=comp,
                                   merge=mergable)
    return redirect(url_for("welcome"))


@app.route("/welcome/functions/alter/split", methods=["POST"])
def split():
    """Page for splitting a competition in two"""
    if request.method == "POST":
        comp = get_comp_from_id(request.form.get('compId', 0))
        ages = [x + 1 for x in range(comp['minAge'], comp['maxAge'])]
        return render_template("functions/splitComps.html", is_logged=LOGGED, where="welcome", comp=comp, ages=ages)
    return redirect(url_for("welcome"))


@app.route("/welcome/functions/alter/split/AB", methods=["POST"])
def split_ab():
    """Script to split one competition with one age group into two sub-comps"""
    if request.method == "POST":
        comp_id = request.form.get('compId', 0)
        comp = get_comp_from_id(comp_id)
        split_into_ab(comp)
    return redirect(url_for("welcome"))


@app.route("/welcome/functions/alter/split/age", methods=["POST"])
def split_age():
    """Script to split one competition with many age groups into two sub-comps"""
    if request.method == "POST":
        comp_id = request.form.get('compId', 0)
        age = int(request.form.get('age', -1))
        comp = get_comp_from_id(comp_id)
        split_by_age(comp, age)
    return redirect(url_for("welcome"))


@app.route("/welcome/functions/choose", methods=["POST"])
def choose_comp_type():
    """The page displaying the competition types to show
    TODO: Merge with show_comps, that'd be cool"""
    if request.method == "POST":
        comp_types = ["Main", "Treble Reel", "Figure", "Art", "Special"]
        return render_template("functions/pickCompType.html", is_logged=LOGGED, where="welcome",
                               comp_types=comp_types, feis_id=request.form.get('feisId', 0))
    return redirect(url_for("welcome"))


@app.route("/welcome/functions/choose/show", methods=["POST"])
def show_comps():
    """The Page displaying all competitions of the given type"""
    if request.method == "POST":
        feis_id, comp_type = request.form.get('feisId'), request.form.get('type')
        titles, tables = make_titles_tables_for(feis_id, comp_type)
        return render_template("functions/showCompType.html", is_logged=LOGGED, where="welcome", titles=titles,
                               tables=tables)
    return redirect(url_for("welcome"))


@app.route("/welcome/functions/scoresheet", methods=["POST"])
def score_calc():
    """The Scoresheet calculator page"""
    if request.method == "POST":
        feis_id = request.form.get('feisId', 0)
        comps = get_comps_from_feis_id(feis_id)
        sheets, total = get_sheets_for_comps(comps)
        return render_template("functions/scoresheetCalc.html", is_logged=LOGGED, where="welcome", sheets=sheets,
                               total=total)
    return redirect("welcome")
