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
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts, title='Home')


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


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # Get post data
        post = Post(title=form.title.data, content=form.content.data, author=current_user)

        # Add post to database
        db.session.add(post)
        db.session.commit()

        # Display success and redirect to home page
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    
    return render_template('create_post.html', title='New post', form=form, legend='Update post')


@app.route("/post/<int:post_id>")
def post(post_id):
    # Get post from database
    post = Post.query.get_or_404(post_id)

    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    # Get post from database
    post = Post.query.get_or_404(post_id)

    # Check if author is current user
    if post.author != current_user:
        abort(403)

    # Update database
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET': # Fill update form with post title and content
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title='Update post', form=form, legend='Update post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
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
