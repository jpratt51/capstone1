from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import InputRequired, Email, NumberRange, Length


class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8)])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class BookshelfForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    subject = StringField("Subject")

# class BookForm(FlaskForm):
#     title = StringField("Title", validators=[InputRequired(message="Must provide book title")])
#     author = StringField("Author", validators=[InputRequired(message="Must provide book author")])
#     subject = StringField("Subject")
#     publish_year = StringField("Publish Year")

class SubjectForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])

class AuthorForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name")

class RateAndReviewForm(FlaskForm):
    rating = StringField("Rating", validators=[InputRequired(), NumberRange(min=1, max=5, message="Rating must be 1-5")])
    review = StringField("Last Name")

class SendCodeForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email(message="Must provide valid email")])

class VerifyEmailForm(FlaskForm):
    code = IntegerField("Code", validators=[InputRequired()])

class SearchForm(FlaskForm):
    book_title = StringField("Book Title")
    author = StringField("Author")
    



