from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, SelectField, SelectMultipleField, FileField
from wtforms.validators import DataRequired, NumberRange, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Register')

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1000, max=2100)])
    publisher = StringField('Publisher', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    pages = IntegerField('Pages', validators=[DataRequired(), NumberRange(min=1)])
    genres = SelectMultipleField('Genres', coerce=int)
    cover = FileField('Cover')
    submit = SubmitField('Save')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        (5, 'Отлично'),
        (4, 'Хорошо'),
        (3, 'Удовлетворительно'),
        (2, 'Неудовлетворительно'),
        (1, 'Плохо'),
        (0, 'Ужасно')
    ], coerce=int)
    text = TextAreaField('Review Text', validators=[DataRequired()])
    submit = SubmitField('Submit')