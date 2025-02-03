
from flask import flash, Flask, redirect, render_template, url_for
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'cbc57430ab3776309a656ca0c6db92eb'

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
        flash(f'Account created for {form.username.data}', 'success')
        return redirect(url_for('home'))
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

if __name__ == '__main__':
    app.run(debug=True)
