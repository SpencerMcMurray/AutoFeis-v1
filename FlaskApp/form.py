from wtforms import Form, StringField, PasswordField, validators, SubmitField


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


class FeisFcnsForm(Form):
    submit = SubmitField('Feis Functions')


class EditDancerForm(Form):
    submit = SubmitField('Edit Dancer')


class AddDancerForm(Form):
    submit = SubmitField('Add a Dancer')


class AddFeisForm(Form):
    submit = SubmitField('Add a Feis')
