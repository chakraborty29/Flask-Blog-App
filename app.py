from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Articles
import mysql.connector
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SubmitField
from wtforms.fields.html5 import EmailField
from flask_wtf import FlaskForm
from passlib.hash import sha256_crypt
import mysql.connector
import os
from functools import wraps
import sys
sys.path.append(
    '/Users/raul/anaconda3/envs/pyfinance/lib/python3.9/site-packages')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)



mydb = mysql.connector.connect(
    host="{HOST}",
    user="{ADMIN}",
    passwd="{PASSSORD}",
    database="{DATABASE_NAME}"
)


# Articles = Articles()


################################################################################################################
# Forms
class RegisterForm(FlaskForm):
    first_name = StringField(
        'First Name', [validators.Length(min=1, max=100)])
    last_name = StringField('Last Name', [validators.Length(min=1, max=200)])
    username = StringField('Username', [validators.Length(min=4)])
    email = EmailField('Email', [validators.Email(),
                                 validators.Length(max=384)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=6, max=100)
    ])
    confirm = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo('password', message='Passwords do not match')
    ])
    submit_button = SubmitField('register')


class LoginForm(FlaskForm):
    email = EmailField(
        'Email', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
    ])
    submit_button = SubmitField('login')


class ArticleForm(FlaskForm):
    heading = StringField('Title', validators=[validators.DataRequired()])
    subheading = StringField('Subheading', validators=[
                             validators.DataRequired()])
    article = TextAreaField('Write Blog Post')
    # tags = StringField('Tags')
    submit_button = SubmitField('post')

################################################################################################################

# Home Route


@app.route('/')
@app.route('/index')
def index():
    cur = mydb.cursor(dictionary=True)
    cur.execute("SELECT * FROM articles")
    data = cur.fetchall()
    Articles = data[::-1]
    cur.close()
    return render_template('index.html', articles=Articles)

# About Route


@app.route('/about')
def about():
    return render_template('about.html')

# Demo Article Route


# Article Route
@app.route('/post/<string:id>/')
def blog_post(id):
    # Create Cursor
    cur = mydb.cursor(dictionary=True)
    cur.execute("SELECT * FROM articles WHERE article_id = %s", [id])
    data = cur.fetchall()

    title = data[0]['title']
    subheading = data[0]['subheading']
    author = data[0]['author']
    create_date = data[0]['create_date']
    content = data[0]['content']

    cur.close()
    return render_template('blog_post.html', id=id, title=title, subheading=subheading, author=author, create_date=create_date, content=content)


# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    login_form = LoginForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.hash(str(form.password.data))

        role = 'user'
        # if username == 'raulc.29':
        #     role = 'admin'
        # else:
        #     role = 'user'

        # Create cursor
        cur = mydb.cursor()
        # Execute query
        cur.execute("INSERT INTO blog_users(username, first_name, last_name, email, password, role) VALUES(%s, %s, %s, %s, %s, %s)",
                    (username, first_name, last_name, email, password, role))
        # Commit to DB
        mydb.commit()
        # Close connection
        cur.close()
        flash('You are now registered and can log in', 'success')

        return redirect(url_for('register'))
    # else:
        # flash('You are missing fields, please correct them and register again', 'danger')

    return render_template('register.html', form=form, login_form=login_form)


# User Login
@app.route('/login', methods=['POST'])
def login():
    form = RegisterForm()
    login_form = LoginForm()
    # print(login_form.validate_on_submit())
    # print(login_form.validate())

    if login_form.validate_on_submit():
        email = login_form.email.data
        password_candidate = login_form.password.data

        # Create Cursor
        cur = mydb.cursor(dictionary=True)

        # Get user by email
        cur.execute("SELECT * FROM blog_users WHERE email = %s", [email])
        data = cur.fetchall()
        if len(data) > 0:
            # Get stored hash
            password = data[0]['password']
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passes
                session['logged_in'] = True
                session['email'] = email
                session['username'] = data[0]['username']
                session['first_name'] = data[0]['first_name']
                session['last_name'] = data[0]['last_name']
                session['role'] = data[0]['role']

                if session['role'] == 'admin':
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('index'))
                # return render_template('register.html', success=success,  form=form, login_form=login_form)
            else:
                error = 'Invalid password'
                flash(error, 'danger')
                return render_template('register.html', form=form, login_form=login_form)
            # Close Databse Connection
            cur.close()
        else:
            error = 'Email not found'
            flash(error, 'danger')
            return render_template('register.html', form=form, login_form=login_form)
    return render_template('register.html', form=form, login_form=login_form)

# Check if user logged in


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('register'))
    return wrap


# Check if user is admin
def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['role'] == 'admin':
            return f(*args, **kwargs)
        else:
            # flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('index'))
    return wrap


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('register'))


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def dashboard():
    form = ArticleForm()

    if request.method == 'POST':
        article = form.article.data
        title = form.heading.data
        subheading = form.subheading.data
        author = session['first_name'] + ' ' + session['last_name']

        # create cursor
        cur = mydb.cursor()

        # Execute
        cur.execute("INSERT INTO articles(title, subheading, author, content) VALUES(%s, %s, %s, %s)",
                    (title, subheading, author, article))

        # Commit to Database
        mydb.commit()

        # Close Connection
        cur.close()
        flash()
        return render_template('demo_post.html', content=article, title=title, subheading=subheading)

    return render_template('dashboard.html', form=form)


if __name__ == '__main__':

    app.run(debug=True, host='192.168.1.2', port='5000')


# create table blog_users (
#     user_id INT NOT NULL AUTO_INCREMENT,
#     username VARCHAR(100) NOT NULL,
#     first_name VARCHAR(100) NOT NULL,
#     last_name VARCHAR(200) NOT NULL,
#     email VARCHAR(384) NOT NULL,
#     password VARCHAR(100) NOT NULL,
#     role VARCHAR(100) NOT NULL,
#     PRIMARY KEY ( user_id )
# );

# CREATE TABLE articles (
#     article_id INT NOT NULL AUTO_INCREMENT,
#     title VARCHAR(255) NOT NULL,
#     subheading VARCHAR(255) NOT NULL,
#     author VARCHAR(300) NOT NULL,
#     content TEXT,
#     create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     PRIMARY KEY ( article_id )
# );
