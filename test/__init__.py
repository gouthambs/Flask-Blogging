import unittest
from flask import Flask
from flask_login import UserMixin

__author__ = 'gbalaraman'


class FlaskBloggingTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = "test-secret"
        self.app.config["WTF_CSRF_ENABLED"] = False  # to bypass CSRF token
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.client = self.app.test_client()

        @self.app.route("/")
        def index():
            return "Hello World!"


class TestUser(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
