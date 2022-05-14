from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo


class RegistrationForm(FlaskForm):
    name = StringField('username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password1 = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Potwierdź Password', validators=[
                              DataRequired(), EqualTo('password1')])
    submit = SubmitField('Zarejestruj się')


class LoginForm(FlaskForm):
    style = {'class': 'ourClasses', 'style': 'width:50%;'}
    email = StringField(
        'Adres e-mail', validators=[DataRequired(), Email(message="Nieprawidłowy email")])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj')


class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Wyślij')
