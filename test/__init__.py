__author__ = 'gbalaraman'

import unittest
from flask import Flask


class FlaskBloggingTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = "test-secret"
        self.app.config["WTF_CSRF_ENABLED"] = False  # to bypass CSRF token check
        self.client = self.app.test_client()

        @self.app.route("/")
        def index():
            return "Hello World!"

