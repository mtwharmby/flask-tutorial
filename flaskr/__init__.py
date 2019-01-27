import os

from flask import Flask

'''
To run the application:
- under Windows
set FLASK_APP=flaskr
set FLASK_ENV=development
flask run

- under Linux:
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
'''


def create_app(test_config=None):
    # This is the application factory
    # Create and configure the app (Flask instance)
    app = Flask(__name__, instance_relative_config=True) # Config files located relative to the instance dir
    # The instance dir should not be under version control and can stor deployment instance specific configs
    app.config.from_mapping( # Default configs
        SECRET_KEY='dev', # Keep data safe; override in production with random value
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite') # Location of SQLite db; in this case in the instance dir
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True) # Override default config values using config.py; could set here SECRET_KEY for production for example
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config) # For tests, provide specific config independent values, rather than instance config

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path) # Ensure the instance dir exists so db can be created; instance dir not created by default
    except OSError:
        pass

    # A simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello world'

    return app