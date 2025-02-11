from flask import abort, flash, redirect, render_template, request, url_for
from flaskblog import app, bcrypt, db
from flaskblog.forms import LoginForm, PostForm, RegistrationForm, UpdateAccount
from flaskblog.models import User, Post
from flask_login import current_user, login_required, login_user, logout_user
import os
from PIL import Image
import secrets


@app.route("/")
@app.route("/home")
def home():
    '''The home page.'''

    # Fetch the first page of posts, ordered by date posted (descending).
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts, title='Home')


@app.route("/about")
def about():
    '''The about page.'''

    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    '''Registers a new account.'''

    # Redirect to the home page if the user is already logged in.
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    # Fetch the data from the registration form, hashing the password, and adding the new account to the database.
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
    '''Logs the user in.'''

    # Redirect to the home page if the user is already logged in.
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    # Fetch the data from the login form, checking if an account exists with the given credentials. Log in the user if it does.
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
    '''Logs the user out.'''

    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    '''Updates a user's profile picture'''

    # Delete the current profile picture from the 'server'.
    prev_picture = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
    if not prev_picture.endswith('default.jpg'):
        os.remove(prev_picture)

    # Encode the image name to a random hex.
    random_hex = secrets.token_hex(8)

    # Assemble the path and filename of the new image with the hexed name.
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_file_name = random_hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_file_name)

    # Resize the image.
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    # Save and return the new, resized image.
    i.save(picture_path)
    return picture_file_name

@app.route("/account", methods=['GET', 'POST'])
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
        return redirect(url_for('account'))
    # Fill the form with the current username and email of the user.
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    '''Make a new post.'''

    form = PostForm()
    if form.validate_on_submit():
        # Fetch title, content and the author from the form.
        post = Post(title=form.title.data, content=form.content.data, author=current_user)

        # Add the post to the database.
        db.session.add(post)
        db.session.commit()

        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    
    return render_template('create_post.html', title='New post', form=form, legend='Update post')


@app.route("/post/<int:post_id>")
def post(post_id):
    '''Opens the post on a new page.'''
    # Fetch the post from the database or return a 404 error if not found
    post = Post.query.get_or_404(post_id)

    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    '''Updates a post.'''

    # Fetch the post from the database or return a 404 error if not found
    post = Post.query.get_or_404(post_id)

    # Check if the author is the current user
    if post.author != current_user:
        abort(403)

    # Update database with the updated post
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET': # Fill the update form with the post's current title and content
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title='Update post', form=form, legend='Update post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    '''Deletes a post.'''

    # Get post from database
    post = Post.query.get_or_404(post_id)

    # Check if author is current user
    if post.author != current_user:
        abort(403)
    
    # Delete post from database
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')

    return redirect(url_for('home'))


@app.route("/user/<string:username>")
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
