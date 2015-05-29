import os
import tempfile
from flask.ext.sqlalchemy import SQLAlchemy
from flask_blogging.sqlastorage import SQLAStorage
from flask_blogging import BloggingEngine
from test import FlaskBloggingTestCase
from flask_login import UserMixin

class TestUser(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


class TestViews(FlaskBloggingTestCase):

    def _create_db(self):
        temp_dir = tempfile.gettempdir()
        self._dbfile = os.path.join(temp_dir, "temp.db")
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+self._dbfile
        self._db = SQLAlchemy(self.app)

    def _create_storage(self, db):
        self.storage = SQLAStorage(db)

    def setUp(self):
        FlaskBloggingTestCase.setUp(self)
        self._create_db()
        self._create_storage(self._db)
        self.engine = BloggingEngine(self.app, self.storage)
        for i in range(20):
            tags = ["hello"] if i < 10 else ["world"]
            user = "testuser" if i<10 else "newuser"
            self.storage.save_post(title="Sample Title%d" % i, text="Sample Text%d" % i,
                                   user_id=user, tags=tags)

            @self.engine.user_loader
            def load_user(user_id):
                return TestUser(user_id)

    def tearDown(self):
        os.remove(self._dbfile)

    def test_index(self):
        response = self.client.get("/blog/")
        self.assertTrue(response.status_code, 200)

        response = self.client.get("/blog")
        self.assertTrue(response.status_code, 301)

    def test_post_by_id(self):
        response = self.client.get("/blog/page/1/")
        self.assertTrue(response.status_code, 200)

        response = self.client.get("/blog/page/1/sample-title/")
        self.assertTrue(response.status_code, 200)

        response = self.client.get("/blog/page/1")  # trailing slash redirect
        self.assertTrue(response.status_code, 200)

    def test_post_by_tag(self):
        response = self.client.get("/blog/tag/hello/")
        self.assertTrue(response.status_code, 200)

        response = self.client.get("/blog/page/hello/5/")
        self.assertTrue(response.status_code, 200)

        response = self.client.get("/blog/page/hello/5/10/")
        self.assertTrue(response.status_code, 200)


