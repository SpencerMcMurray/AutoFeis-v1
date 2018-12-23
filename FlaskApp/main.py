import os
import functions as f
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


@app.route("/")
def index():
    """The index page"""
    return render_template("index.html", is_logged=LOGGED, where="home", function=f.display_feis)


@app.route("/about")
def about():
    """The about page"""
    return render_template("about.html", is_logged=LOGGED, where="about")


@app.route("/info")
def feisinfo():
    """The Feis info page"""
    feiseanna = f.get_all_feiseanna()
    return render_template("feisInfo.html", is_logged=LOGGED, where="feisinfo", feiseanna=feiseanna)


@app.route("/results")
def results():
    """The results page"""
    return render_template("results.html", is_logged=LOGGED, where="results", function=f.display_all_results)


@app.route("/entries/<int:feis>")
def entries(feis):
    """The entries page
    TODO: Take away id from url"""
    return render_template("entries.html", is_logged=LOGGED, where="feisinfo", entries=f.get_entries_from_feis(feis),
                           name=f.feis_name_from_id(feis))


@app.route("/register", methods=["GET", "POST"])
def register():
    """The register page"""
    if request.method == "POST":
        if request.form.get("startScript", None) is None:
            session['feis_id'] = request.form.get("id", -1)
        # Get the feis info and all the user's dancers
        feis = f.get_feis_with_id(session['feis_id'])
        dancers = f.get_dancers_with_user(f.get_id_from_email(session['email']))

        if request.form.get("startScript", None) is not None:
            for dancer in dancers:
                f.register(request.form.getlist('register[' + str(dancer['id']) + '][]'),
                           feis['id'], dancer['id'])
            session.pop('feis_id')
            return redirect(url_for('welcome'))

        comps = f.get_all_comps_for_dancers(session['feis_id'], dancers)

        return render_template("registration/registerFor.html", is_logged=LOGGED, where="register",
                               feis_name=feis['name'], dancers=dancers, comps=comps)
    feiseanna = f.get_all_feiseanna()
    return render_template("registration/register.html", is_logged=LOGGED, where="register", feiseanna=feiseanna)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """The sign up page"""
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():

        # Check if the email given already exists
        if f.email_taken(form.email.data):
            flash("The email provided already belongs to a user")
            return render_template("signUp.html", form=form, is_logged=LOGGED, where="signup")

        # Otherwise sign the user up
        f.sign_up(form.email.data, form.password.data, form.f_name.data, form.l_name.data)
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
        if not f.email_taken(form.email.data):
            flash("The email provided doesn't belong to a user")
            return render_template("logIn.html", form=form, is_logged=LOGGED, where="login")
        # Make sure the password matches the email given in the database
        if not f.validate(form.email.data, form.password.data):
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

    user_id = f.get_id_from_email(session['email'])
    dancers = f.get_dancers_with_user(user_id)
    feiseanna = f.get_feiseanna_with_forg(user_id)
    if request.method == 'POST':
        if request.form.get('submit', None) == "Add a Dancer":
            return redirect(url_for("add_dancer"))

        if request.form.get('submit', None) == "Add a Feis":
            return redirect(url_for("add_feis"))
    return render_template("welcome.html", is_logged=LOGGED, where="welcome", email=session["email"],
                           dancers=dancers,
                           feiseanna=feiseanna,
                           edit_dancer=edit_dancer_form,
                           dancer_form=add_dancer_form,
                           feis_form=add_feis_form,
                           feis_fcns_form=feis_fcns_form,
                           function=f.display_name)


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
            choices = f.age_dropdown(session.get('single_ages'))
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
            comps = f.get_comps_from_session(session)

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
            session['comps'] = f.serialize_comps(comps)

            return render_template("createFeis/addFeisShow.html", is_logged=LOGGED, where='welcome', comps=comps)

        if request.form.get('next') == 'info':
            # TODO: Implement file validity checks
            info_form = FeisInfoForm(request.form)
            return render_template("createFeis/addFeisInfo.html", is_logged=LOGGED, where='welcome', form=info_form)

        if request.form.get('next') == 'create':
            # TODO: Include pay-wall here

            # Create feis
            feis_id = f.create_feis(f.get_id_from_email(session['email']), request.form.get('name'),
                                    request.form.get('date'), request.form.get('location'), request.form.get('region'),
                                    request.form.get('website'))

            # Upload file
            file = request.files['syllabus']
            f.upload_file(file, feis_id, app.config["UPLOAD_FOLDER"])

            # Create all competitions
            f.create_comps(feis_id, f.deserialize_comps(session['comps']))
            session.pop('comps')
            return redirect(url_for('welcome'))

    return render_template("createFeis/addFeisStart.html", is_logged=LOGGED, where='welcome', form=traits)


@app.route("/welcome/add_dancer", methods=['GET', 'POST'])
def add_dancer():
    """The add dancer page"""
    form = CreateDancer(request.form)
    if request.method == "POST" and form.validate():
        f.create_dancer(f.get_id_from_email(session['email']), form.f_name.data, form.l_name.data, form.school.data,
                        int(form.year.data), form.level.data, form.gender.data, int(form.show.data))
        return redirect(url_for("welcome"))

    return render_template("createDancer/addDancer.html", is_logged=LOGGED, where="welcome", form=form)


@app.route("/welcome/delete_dancer", methods=['POST'])
def delete_dancer():
    """The path through deleting a dancer"""
    if request.method == "POST":
        f.delete_dancer_from_id(request.form.get('id', 0))
    return redirect(url_for('welcome'))


@app.route("/welcome/edit_dancer", methods=['POST'])
def edit_dancer():
    """The edit dancer page for a given dancer"""
    # TODO: Add current info as default input values
    if request.method != "POST":
        return redirect(url_for('welcome'))
    form = CreateDancer(request.form)
    dancer = f.get_dancer_from_id(request.form.get('dancerId', 0))
    return render_template("createDancer/editDancer.html", is_logged=LOGGED, where="welcome", dancer=dancer, form=form)


@app.route("/welcome/edit_dancer/alter", methods=["POST"])
def alter_dancer():
    """The path through altering a dancer"""
    if request.method != "POST":
        return redirect(url_for('welcome'))
    f.alter_dancer(request.form.get('id', -1), request.form.get('f_name', ''), request.form.get('l_name', ''),
                   request.form.get('school', ''),  request.form.get('year', -1), request.form.get('level', ''),
                   request.form.get('gender', ''), int(request.form.get('show', -1)))
    return redirect(url_for('welcome'))


@app.route("/welcome/functions", methods=['POST'])
def feis_functions():
    """The feis functions for a given feis"""
    if request.method == "POST":
        name = f.feis_name_from_id(request.form.get('feisId', 0))
        return render_template("feisFunctions.html", is_logged=LOGGED, where="welcome", name=name)
    return redirect(url_for('welcome'))
