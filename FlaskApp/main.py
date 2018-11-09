import os
import functions as f
from form import *
from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash, session
app = Flask(__name__)
app.secret_key = os.urandom(24)
# TODO: Implement flask_login?
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


@app.route("/feisinfo")
def feisinfo():
    """The Feis info page"""
    return render_template("feisInfo.html", is_logged=LOGGED, where="feisinfo", function=f.display_all_feiseanna)


@app.route("/results")
def results():
    """The results page"""
    return render_template("results.html", is_logged=LOGGED, where="results", function=f.display_all_results)


@app.route("/register")
def register():
    """The register page"""

    return render_template("register.html", is_logged=LOGGED, where="register", function=f.display_open_feiseanna)


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
    """The welcome page"""
    feis_fcns_form = FeisFcnsForm(request.form)
    edit_dancer_form = EditDancerForm(request.form)
    add_dancer_form = AddDancerForm(request.form)
    add_feis_form = AddFeisForm(request.form)

    user_id = f.get_id_from_email(session['email'])
    dancers = f.get_dancers_with_user(user_id)
    feiseanna = f.get_feiseanna_with_forg(user_id)
    if request.method == 'POST':
        if request.form.get('submit', None) == "Feis Functions":
            return redirect(url_for('feis_functions', id=int(request.form.get('id', -1))))

        if request.form.get('submit', None) == "Edit Dancer":
            return redirect(url_for('edit_dancer', id=int(request.form.get('id', -1))))

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
    return render_template("tos.html", is_logged=LOGGED, where="signup")


@app.route("/welcome/add_feis")
def add_feis():
    pass


@app.route("/welcome/add_dancer", methods=['GET', 'POST'])
def add_dancer():
    """The add dancer page"""
    form = CreateDancer(request.form)
    if request.method == "POST" and form.validate():
        f.create_dancer(f.get_id_from_email(session['email']), form.f_name.data, form.l_name.data, form.school.data,
                        int(form.year.data), form.level.data, form.gender.data, int(form.show.data))
        return redirect(url_for("welcome"))

    return render_template("addDancer.html", is_logged=LOGGED, where="welcome", form=form)


@app.route("/welcome/edit_dancer", methods=['GET', 'POST'])
def edit_dancer():
    pass


@app.route("/welcome/functions")
def feis_functions():
    """The feis functions for a given feis"""
    html = f.feis_functions_html(request.args['id'])
    return render_template_string(html, is_logged=LOGGED, where="welcome")
