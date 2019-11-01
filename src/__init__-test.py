'''
Name:		__init__.py
Purpose:	Implement the application factory function

Author:	Wim

Created:	1/11/2019
Copyright:	(c) Wim 2019
Licence:
'''

from flask import Flask

# Globally accessible libraries
# ---- libraries should come here ----


def create_app():
    # create and configure the portal application
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    # Initialize Plugins
    # ---- plugin init statement should come here ----

    with app.app_context():
        # Include our Routes
        from . import routes

        # Register Blueprints
        # ---- blueprints should come here ----

    return app