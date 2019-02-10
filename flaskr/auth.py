import functools

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db


# Create a Blueprint named auth. Blueprints organise linked/related functions
# e.g. this module will add authorisation functionality to this app, including
# login, logout, checking user is authenticated, getting the authenticated user
bp = Blueprint('auth', __name__, url_prefix='/auth')


# Associates auth/register URL with this method
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':  # If user submitted a form...
        # request.form is a dict which maps form values to and keys
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Next two part of the 'if' check username & password are not empty
        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif db.execute('SELECT id FROM user WHERE username = ?',
                        (username,)).fetchone() is not None:
            # Is the username already stored in the db? Return only one line
            # from query, regardless how many were returned
            error = 'User {} is already registered'.format(username)

        if error is None:
            # Assuming username/password are OK, put them into the db
            db.execute('INSERT INTO user (username, password) VALUES (?, ?)',
                       (username, generate_password_hash(password)))
            db.commit()  # This effectively flushes the db
            return redirect(url_for('auth.login'))
            # url_for takes an endpoint, which is based on the function name
            # generating the view. Args can be passed. e.g.:
            #   url_for('hello', who='world')
            # hello is the function; who is an argument; world is value for arg
            #
            # With blueprints, the name of the blueprint is prepended

        flash(error)
        # Flash is a way to render simple messages in case of, for example, an
        # error

    # In all cases except successful registration of a user, pass back the html
    # registration template
    return render_template('auth/register.html')


# Similar structure to the method above; when the user calls this method as a
# POST with a valud username and password, send to the homepage with an active
# session; otherwise generate the login page and indicate the error.
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM user WHERE username = ?',
                          (username,)).fetchone()
        # Store user (lifted from db) in a variable for later use; also
        # contains password

        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        if error is None:
            # Session is a dict storing info across requests; held as a cookie
            # which is passed back & forth by user's browser
            session.clear()
            session['user_id'] = user['id']  # Add 'user_id' to session
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# Function used to make user name/id etc. available across multiple requests
# Register a function called before the view function, regardless of the URL
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?',
                                  (user_id,)).fetchone()


# Log user out of session - just clear the session cookie (removes user_id)
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# We need to know if the user is logged in when, e.g. editing
# This decorator will check for a logged in user and redirect to the login page
# if none is found. If a user is logged in, return the requested view
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
