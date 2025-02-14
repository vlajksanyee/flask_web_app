
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flaskblog import app, bcrypt, db, mail
from flaskblog.models import Post
from flaskblog.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
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
        return redirect(url_for('main.home'))
    
    return render_template('create_post.html', title='New post', form=form, legend='Update post')


@posts.route("/post/<int:post_id>")
def post(post_id):
    '''Opens the post on a new page.'''
    # Fetch the post from the database or return a 404 error if not found
    post = Post.query.get_or_404(post_id)

    return render_template('post.html', title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
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
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET': # Fill the update form with the post's current title and content
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title='Update post', form=form, legend='Update post')

@posts.route("/post/<int:post_id>/delete", methods=['POST'])
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

    return redirect(url_for('main.home'))
