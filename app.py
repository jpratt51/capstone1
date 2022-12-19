"""Flask app for MyReads"""

from flask import Flask, redirect, session, flash, render_template
from models import db, connect_db, User
from forms import UserForm, LoginForm, SendCodeForm, VerifyEmailForm, SearchForm
from flask_mail import Mail, Message
from random import randint
from search import book_search
import requests

app = Flask(__name__)

# sqlalchemy config settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///myreads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "secret"

# flask mail config settings
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'myreadsverify@gmail.com'
app.config['MAIL_PASSWORD'] = 'vvztohuzogykuahh'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

verify_code = 0
verified = False
user_email = ""

connect_db(app)

API_BASE_URL = 'http://openlibrary.org/search.json'

@app.route("/")
def myreads_homepage():
    """Render myreads homepage."""

    return render_template("homepage.html")

# Account verification, registration, and login/logout routes:
# *************************************************************************

@app.route("/send-code", methods=["GET","POST"])
def send_code():
    """Generate form to verify user's email account. Sends six digit code to users email that will be used to complete registration form."""

    # Direct user to logout before registering new acccount
    try:
        if session["username"] :
            flash("First log out to register new account", "danger")
            return redirect("/")

    except KeyError:
        form = SendCodeForm()
        if form.validate_on_submit():

            # Check if email is already in use
            u = User.query.filter_by(email=form.email.data).first()

            # If so, redirect user to login page
            if u :
                flash(f"Email already verified", "danger")
                return redirect('/login')

            # Updating global variables to use in code verification route
            global verify_code
            global user_email

            # Generate random 6 digit number
            verify_code = randint(100000,999999)

            # Grab user email from form
            user_email = form.email.data

            # Send email to user with verification code
            msg = Message('Myreads email verification', sender = 'myreadsverify@gmail.com', recipients = [user_email])
            msg.body = f"Verification code: {verify_code}"
            mail.send(msg)

            # Inform user that code has been sent and redirect to code verification route
            flash(f"Verification code sent to {user_email}", "success")
            return redirect('/verify-code')

        # Generate code submission form
        return render_template('send-code.html', form=form)

@app.route("/verify-code", methods=["GET","POST"])
def code_verification():
    """Generate form for user to submit code that was sent to their email for email verification."""

    # Gather code input from valid form submission
    form = VerifyEmailForm()
    if form.validate_on_submit():
        if int(verify_code) == int(form.code.data):

            # Inform user of successful email verification and change verified status to true. Send user to registration page.
            global verified
            verified = True
            flash(f"Success! Email verified.", "success")
            return redirect("/register")
    
    # Generate verification form
    return render_template('verify.html', form=form)

@app.route('/register', methods=["GET", "POST"])
def register_user():
    """Generate form to register new user.

    Upon successful registration add new user username to session for login."""

    global verified

    # make sure user email has been verified
    if verified == True :
        form = UserForm()
        if form.validate_on_submit():
            # reset verification status
            verified = False

            # Check if username is already in use
            u = User.query.filter_by(username=form.username.data).first()

            # If so, redirect user to registration page
            if u :
                flash(f"Username already in use", "info")
                verified = True
                return redirect('/register')

            # Gather form data and user email into user instance
            username = form.username.data
            password = form.password.data
            email = user_email
            first_name = form.first_name.data
            last_name = form.last_name.data
            new_user = User.register(username, first_name, last_name, email,password)

            # Add new user to database and username to session
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username

            # Inform user of successful account creation and redirect to homepage
            flash(f'Welcome {new_user.username}! Account creation successful!', "success")
            return redirect('/')
        # Generate registration form
        return render_template('register.html', form=form)
    # Send user to send code page if email not verified
    return redirect("/send-code")

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Generate form to handle user login."""

    # If user is already logged in, redirect to homepage.
    try:
        if session["username"] :
            flash("You are logged in", "primary")
            return redirect("/")

    except KeyError:
        
        form = LoginForm()

        # Gather form data from valid submission
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            # authenticate credentials
            user = User.authenticate(username, password)
            if user:
                flash(f"Welcome back, {user.username}!", "primary")

                # Set session username to current user. Send user to homepage.
                session['username'] = user.username
                return redirect('/')
            else:
                form.username.errors = ['Invalid username/password.']

        # Generate login form
        return render_template('login.html', form=form)
    

@app.route('/logout')
def logout_user():
    """Logout current user."""

    # Change logged in status to false and remove username from session. Redirect to homepage.
    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/')

# Logged in user routes:
# *************************************************************************

@app.route("/find-books", methods=['GET', 'POST'])
def mylibrary():
    """Render user mylibrary page."""

    # Confirm user logged in
    try:
        session["username"]

    # Else redirect to login page
    except KeyError:
        flash("Must be logged in to view library", "primary")
        return redirect('/login')

    # Continue to mylibrary if user is logged in:
    else:
        form = SearchForm()

        # Gather form data from valid submission
        if form.validate_on_submit():
            book_title = form.book_title.data or ""
            author = form.author.data or ""

            if len(book_title) == 0 and len(author) == 0:
                flash("Please enter book title and/or author", "danger")
                return redirect ("/mylibrary")
  
            book_list = book_search(book_title, author)
            return render_template("search-results.html", books=book_list, form=form)
            
        return render_template("find-books.html", form=form)

@app.route("/add-books", methods=['GET', 'POST'])
def add_book():
    """Generate and handle form to add book to database and update list of user's books."""

    
