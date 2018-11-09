from wtforms import Form, StringField, PasswordField, validators, SubmitField, SelectField
from functions import year_dropdown, school_dropdown


class RegistrationForm(Form):
    f_name = StringField('First Name', [validators.InputRequired(), validators.Length(min=1, max=45)])
    l_name = StringField('Last Name', [validators.InputRequired(), validators.Length(min=1, max=45)])
    email = StringField('Email', [validators.InputRequired(), validators.Length(min=5, max=75), validators.Email()])
    password = PasswordField('Password', [
        validators.InputRequired(), validators.Length(min=6, max=100),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(Form):
    email = StringField('Email', [validators.InputRequired(), validators.Length(min=5, max=75), validators.Email()])
    password = PasswordField('Password', [validators.InputRequired(), validators.Length(min=6, max=100)])


class CreateDancer(Form):
    f_name = StringField('First Name', [validators.InputRequired(), validators.Length(min=1, max=45)])
    l_name = StringField('Last Name', [validators.InputRequired(), validators.Length(min=1, max=45)])
    year = SelectField('Birth Year', choices=year_dropdown())
    school = SelectField('Dance School', choices=school_dropdown())
    level = SelectField('Level', choices=[('Open Championship', 'Open Championship'),
                                          ('Preliminary Championship', 'Preliminary Championship'),
                                          ('Grades-level', 'Grades-level'),
                                          ('Non-Dancer', 'Non-Dancer')])
    gender = SelectField('Gender', choices=[('Female', 'Female'), ('Male', 'Male'), ('Other', 'Other')])
    show = SelectField('Show Online', choices=[('1', 'Show'), ('0', 'Hide')])


class FeisFcnsForm(Form):
    submit = SubmitField('Feis Functions')


class EditDancerForm(Form):
    submit = SubmitField('Edit Dancer')


class AddDancerForm(Form):
    submit = SubmitField('Add a Dancer')


class AddFeisForm(Form):
    submit = SubmitField('Add a Feis')
