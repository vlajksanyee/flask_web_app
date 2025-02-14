
from flask import Blueprint, render_template, request
from flaskblog.models import Post

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    '''The home page.'''

    # Fetch the first page of posts, ordered by date posted (descending).
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts, title='Home')


@main.route("/about")
def about():
    '''The about page.'''

    return render_template('about.html', title='About')
