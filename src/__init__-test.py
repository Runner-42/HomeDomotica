'''
Name:		__init__.py
Purpose:	Implement the application factory function

Author:	Wim

Created:	1/11/2019
Copyright:	(c) Wim 2019
Licence:
'''

import OS
from flask import Flask

# Globally accessible libraries
# ---- libraries should come here ----


def create_app():
    # create and configure the portal application
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    # Initialize Plugins
    # ---- plugin init statement should come here ----

    @app.route('/hello')
    def hello_world():
        return "<h1 style='color:blue'>Hello There!</h1>"

    return app