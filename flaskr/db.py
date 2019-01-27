import sqlite3

import click # Something similar to argparse...
from flask import current_app, g # g is unique data store for each request; current_app is Flask app handling the request
# N.B. There is no application object since __init__.py is an app factory; need current_app to get the app object
from flask.cli import with_appcontext

'''
DB access is handled based on connections. In web applications, connections are tied 
to a requests. Connection is created at some point when handling a web request and 
closed before the response is sent. 
'''


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'], # Connect to a db at the location given in __init__.py
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row # Return rows that behave like dicts

    return g.db


# N.B. Needs to be registered with app! See init_app
def close_db(e=None):
    db = g.pop('db', None) # Is there a db member in g? If not, set to None, otherwise set to db

    if db is not None:
        db.close()


def init_db():
    db = get_db() # Getting the open db using the call above

    with current_app.open_resource('schema.sql') as f: # Open file relative to flaskr package
        db.executescript(f.read().decode('utf8'))


# N.B. Needs to be registered with app! See init_app
@click.command('init-db')
@with_appcontext
def init_db_command():
    ''' Clear the existing data and create new tables. '''
    init_db()
    click.echo('Initialised the database.')


# Because using an app factory, app instance not available. This function can be called from the factory though, providing the app instance as an argument
def init_app(app):
    app.teardown_appcontext(close_db) # Call this function when cleaning up after returning response
    app.cli.add_command(init_db_command) # Add function that can be called with flask command