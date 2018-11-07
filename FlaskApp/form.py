from wtforms import Form, StringField, PasswordField, validators


class RegistrationForm(Form):
    f_name = StringField('First Name', [validators.DataRequired(), validators.Length(min=1, max=45)])
    l_name = StringField('Last Name', [validators.DataRequired(), validators.Length(min=1, max=45)])
    email = StringField('Email', [validators.DataRequired(), validators.Length(min=1, max=75)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(Form):
    email = StringField('Email', [validators.DataRequired(), validators.Length(min=1, max=75)])
    password = PasswordField('Password', [validators.DataRequired()])
