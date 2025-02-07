from flask import flash, redirect, render_template, url_for
from flaskblog import app, bcrypt, db
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post

test_posts = [
    {
        'author': 'Alex Butler',
        'title': 'First test post',
        'content': 'Content of first test post',
        'date_posted': 'February 10, 2025'
    },
    {
        'author': 'Diana Butler',
        'title': 'Second test post',
        'content': 'Content of second test post',
        'date_posted': 'March 05, 2025'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=test_posts, title='Home')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created. You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful! Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)