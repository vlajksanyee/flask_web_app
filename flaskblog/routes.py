from flask import flash, redirect, render_template, request, url_for
from flaskblog import app, bcrypt, db
from flaskblog.forms import LoginForm, RegistrationForm, UpdateAccount
from flaskblog.models import User, Post
from flask_login import current_user, login_required, login_user, logout_user
import os
from PIL import Image
import secrets

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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful! Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    # Delete previous picture
    prev_picture = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
    if not prev_picture.endswith('default.jpg'):
        os.remove(prev_picture)

    # Hex image name
    random_hex = secrets.token_hex(8)

    # Get path
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_file_name = random_hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_file_name)

    # Resize image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    # Save and return resized image
    i.save(picture_path)
    return picture_file_name

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccount()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)
