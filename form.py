from wtforms import Form, StringField, PasswordField, validators, SubmitField, SelectField
from functions.createDancer import year_dropdown, school_dropdown
from functions.createFeis import get_regions


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
    email = StringField('Email')
    password = PasswordField('Password')


class CreateDancer(Form):
    f_name = StringField('First Name', [validators.InputRequired()])
    l_name = StringField('Last Name', [validators.InputRequired()])
    year = SelectField('Birth Year', choices=year_dropdown())
    school = SelectField('Dance School', choices=school_dropdown())
    level = SelectField('Level', choices=[('Open Championship', 'Open Championship'),
                                          ('Preliminary Championship', 'Preliminary Championship'),
                                          ('Grades', 'Grades-level'),
                                          ('Non-Dancer', 'Non-Dancer')])
    gender = SelectField('Gender', choices=[('Female', 'Female'), ('Male', 'Male'), ('Other', 'Other')])
    show = SelectField('Show Online', choices=[('1', 'Show'), ('0', 'Hide')])


class ChooseTraitsForm(Form):
    single_ages = SelectField('Single Age Groups', choices=[("1", "Yes"), ("0", "No")])
    levels = SelectField('Have Levels?', choices=[("1", "Yes"), ("0", "No")])
    separate_by_sex_champ = SelectField('Separate Main Championship-Level Competitions By Sex',
                                        choices=[("1", "Yes"), ("0", "No")])
    separate_by_sex_grades = SelectField('Separate Main Grades-Level Competitions By Sex',
                                         choices=[("1", "Yes"), ("0", "No")])


class FeisInfoForm(Form):
    name = StringField("Feis Name", [validators.InputRequired()])
    location = StringField("Location of Feis", [validators.InputRequired()])
    region = SelectField("Region of Feis", choices=get_regions())
    website = StringField("Website for Feis", [validators.InputRequired()])


class FeisFcnsForm(Form):
    submit = SubmitField('Feis Functions')


class EditDancerForm(Form):
    submit = SubmitField('Edit Dancer')


class AddDancerForm(Form):
    submit = SubmitField('Add a Dancer')


class AddFeisForm(Form):
    submit = SubmitField('Add a Feis')
