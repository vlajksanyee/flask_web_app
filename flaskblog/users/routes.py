
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flaskblog import bcrypt, db
from flaskblog.models import Post, User
from flaskblog.users.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, UpdateAccount
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    '''Registers a new account.'''

    # Redirect to the home page if the user is already logged in.
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Fetch the data from the registration form, hashing the password, and adding the new account to the database.
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created. You are now able to log in.', 'success')
        return redirect(url_for('users.login'))
    
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    '''Logs the user in.'''

    # Redirect to the home page if the user is already logged in.
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Fetch the data from the login form, checking if an account exists with the given credentials. Log in the user if it does.
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful! Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    '''Logs the user out.'''

    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    '''A user's account page. Can change username and email on this page.'''

    form = UpdateAccount()
    # Update the user's account if the form is valid.
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    # Fill the form with the current username and email of the user.
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    '''Only displays posts of a given user.'''

    # Get first page
    page = request.args.get('page', 1, type=int)

    # Fetch the user from the database or return a 404 error if not found
    user = User.query.filter_by(username=username).first_or_404()

    # Fetch given user's posts ordered by date posted (descending)
    posts = Post.query\
        .filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    
    return render_template('user_posts.html', posts=posts, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    '''Requests a password reset.'''

    # Redirect to the home page if the user is logged in.
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
        
    return render_template('reset_request.html', title='Reset password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    '''Resets the user's password.'''

    # Redirect to the home page if the user is logged in.
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Check if the token is valid or not
    user: User = User.verify_reset_token(token)
    
    # user is None if the token is invalid
    if user is None:
        flash('Invalid token.', 'warning')
        return redirect(url_for('users.reset_request'))
    
    # Update the user's password
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash(f'Your password has been updated. You are now able to log in with your new password.', 'success')
        return redirect(url_for('users.login'))
    
    return render_template('reset_token.html', title='Reset password', form=form)
