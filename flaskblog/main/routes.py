
from flask import Blueprint, redirect, render_template, request, session
from flaskblog.models import Post

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    '''Route for the home page.'''

    # Fetch the first page of posts, ordered by date posted (descending).
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts, title='Home')


@main.route("/about")
def about():
    '''Route for the about page.'''

    return render_template('about.html', title='About')


@main.get("/toggle-theme")
def toggle_theme():
    '''Route to toggle dark theme on the page.'''

    # Get the current theme and set it to the other if the button is clicked.
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    return redirect(request.args.get("current_page"))
