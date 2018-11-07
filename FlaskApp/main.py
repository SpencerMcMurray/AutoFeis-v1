import functions as f
from form import RegistrationForm, LoginForm
from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash, session
app = Flask(__name__)
app.secret_key = b'\x17\x10IO\xff$\xbe&\xf9X5\x9b\x1c\xea\x0c\xdf'
LOGGED = 'email' in session


@app.route("/")
def index():
    """The index page"""
    return render_template("index.html", is_logged=False, where="home", function=f.display_feis)


@app.route("/about")
def about():
    """The about page"""
    return render_template("about.html", is_logged=False, where="about")


@app.route("/feisinfo")
def feisinfo():
    """The Feis info page"""
    return render_template("feisInfo.html", is_logged=False, where="feisinfo", function=f.display_all_feiseanna)


@app.route("/results")
def results():
    """The results page"""
    return render_template("results.html", is_logged=False, where="results", function=f.display_all_results)


@app.route("/register")
def register():
    """The register page"""

    return render_template("register.html", is_logged=False, where="register", function=f.display_open_feiseanna)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """The sign up page"""
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():

        # Check if the email given already exists
        if f.email_taken(form.email.data):
            flash("The email provided already belongs to a user")
            return render_template("signUp.html", form=form, is_logged=False, where="signup")

        # Otherwise sign the user up
        else:
            f.sign_up(form.email.data, form.password.data, form.f_name.data, form.l_name.data)
            return redirect(url_for('login'))
    return render_template("signUp.html", form=form, is_logged=False, where="signup")


@app.route("/login", methods=["GET", "POST"])
def login():
    """The login page"""
    # If the user is logged in, send them to the welcome page
    if 'email' in session:
        return redirect(url_for("welcome"))
    form = LoginForm()
    if request.method == "POST" and form.validate():

        # Make sure the email is in the database
        if not f.email_taken(form.email.data):
            flash("The email provided doesn't belong to a user")
            return render_template("logIn.html", form=form, is_logged=False, where="login")
        # Make sure the password matches the email given in the database
        if not f.validate(form.email.data, form.password.hash):
            flash("The password given doesn't match with the email provided")
            return render_template("logIn.html", form=form, is_logged=False, where="login")
        # Log the user in
        session['email'] = form.email.data
        return redirect(url_for("welcome"))
    return render_template("logIn.html", form=form, is_logged=False, where="login")


@app.route("/logout")
def logout():
    """The logout page...?"""
    session.pop('email')
    return render_template("index.html", is_logged=True, where="welcome")


@app.route("/welcome")
def welcome():
    """The welcome page"""
    return render_template("welcome.html", is_logged=True, where="welcome", function1=f.display_my_dancers,
                           function2=f.display_my_feiseanna)


@app.route("/terms")
def terms():
    return render_template("tos.html", is_logged=False, where="signup")


@app.route("/welcome/functions")
def feis_functions():
    """The feis functions for a given feis"""
    feis_id = 0
    html = f.feis_functions_html(feis_id)
    return render_template_string(html, is_logged=True, where="welcome")
