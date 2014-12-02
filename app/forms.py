from flask.ext.wtf import Form, RecaptchaField
from app.models import User
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import TextField, BooleanField, SubmitField, PasswordField, StringField, TextAreaField
from wtforms.validators import Required, EqualTo, DataRequired, Length, Email

class LoginForm(Form):
    username = TextField('Username', validators = [DataRequired(), Length(min=3, max=15)])
    password = PasswordField('Password', validators = [DataRequired(), Length(min=5, max=20)])
    remember_me = BooleanField('remember_me', default = False)

class RegisterForm(Form):
	username = TextField("UserName", validators = [DataRequired("Username Field Required"), Length(min=3, max=15)])
	password = PasswordField('New Password', validators = [DataRequired("Password Field Required"), Length(min=5, max=20), EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password')
	email = TextField("Email", validators = [DataRequired("Email Required"), Length(min=6, max=30), Email()])
	recaptcha = RecaptchaField()

class PasswordResetForm(Form):
	password = PasswordField('Password', validators = [Length(min=6, max=20), Required(), EqualTo('password_confirm', message='Confirm password did not match the original password you entered.')])
	password_confirm = PasswordField('Confirm Password', validators = [Length(min=6, max=20), Required()])

class EditTopic(Form):
	topicTitle = TextField("Topic title", validators = [DataRequired("Topic title required")])
	tags = TextField("Tags")
	description = TextAreaField("Description", validators=[DataRequired("Must give a topic description!")])
