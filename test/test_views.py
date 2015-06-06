import os
import tempfile
from flask import redirect
from flask.ext.login import LoginManager, login_user, logout_user, current_user
from sqlalchemy import create_engine
from flask_blogging.sqlastorage import SQLAStorage
from flask_blogging import BloggingEngine
from test import FlaskBloggingTestCase
from flask_login import UserMixin


class TestUser(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


class TestViews(FlaskBloggingTestCase):

    def _create_storage(self):
        temp_dir = tempfile.gettempdir()
        self._dbfile = os.path.join(temp_dir, "temp.db")
        conn_string = 'sqlite:///'+self._dbfile
        engine = create_engine(conn_string)
        self.storage = SQLAStorage(engine)

    def setUp(self):
        FlaskBloggingTestCase.setUp(self)
        self._create_storage()
        self.engine = BloggingEngine(self.app, self.storage,
                                     url_prefix="/blog")
        self.login_manager = LoginManager(self.app)

        @self.login_manager.user_loader
        @self.engine.user_loader
        def load_user(user_id):
            return TestUser(user_id)

        @self.app.route("/login/<username>/", methods=["POST"])
        def login(username):
            this_user = TestUser(username)
            login_user(this_user)
            return redirect("/")

        @self.app.route("/logout/")
        def logout():
            logout_user()
            return redirect("/")

        for i in range(20):
            tags = ["hello"] if i < 10 else ["world"]
            user = "testuser" if i < 10 else "newuser"
            self.storage.save_post(title="Sample Title%d" % i,
                                   text="Sample Text%d" % i,
                                   user_id=user, tags=tags)

    def tearDown(self):
        os.remove(self._dbfile)

    def test_index(self):
        response = self.client.get("/blog/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/blog")
        self.assertEqual(response.status_code, 301)

        response = self.client.get("/blog/5/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/blog/5/2/")
        self.assertEqual(response.status_code, 200)

    def test_post_by_id(self):
        response = self.client.get("/blog/page/1/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/blog/page/1/sample-title/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/blog/page/1")  # trailing slash redirect
        self.assertEqual(response.status_code, 301)

    def test_post_by_tag(self):
        response = self.client.get("/blog/tag/hello/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/blog/tag/hello/5/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/blog/tag/hello/5/2/")
        self.assertEqual(response.status_code, 200)

    def test_post_by_author(self):
        response = self.client.get("/blog/author/newuser/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/blog/author/newuser/5/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/blog/author/newuser/5/2/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/blog/author/nonexistent_user/")
        assert "No posts found for this user!" in response.data

    def test_editor_get(self):
        user_id = "testuser"
        with self.client:
            # access to editor should be forbidden before login
            response = self.client.get("/blog/editor/")
            self.assertEqual(response.status_code, 401)

            response = self.client.get("/blog/editor/1/")
            self.assertEqual(response.status_code, 401)

            self.login(user_id)
            self.assertEquals(current_user.get_id(), user_id)
            response = self.client.get("/blog/editor/")
            assert response.status_code == 200

            for i in range(1, 21):
                # logged in user can edit their post, and will be redirected
                # if they try to edit other's post
                response = self.client.get("/blog/editor/%d/" % i)
                expected_status_code = 200 if i <= 10 else 302
                self.assertEqual(response.status_code, expected_status_code,
                                 "Error for item %d %d" %
                                 (i, response.status_code))
            # logout and the access should be gone again
            self.logout()
            response = self.client.get("/blog/editor/")
            self.assertEqual(response.status_code, 401)

            response = self.client.get("/blog/editor/1/")
            self.assertEqual(response.status_code, 401)

    def test_editor_post(self):
        user_id = "testuser"
        with self.client:
            # access to editor should be forbidden before login
            response = self.client.get("/blog/page/21/",
                                       follow_redirects=True)
            assert "The page you are trying to access is not valid!" \
                   in response.data

            response = self.client.post("/blog/editor/")
            self.assertEqual(response.status_code, 401)

            response = self.client.post("/blog/editor/1/")
            self.assertEqual(response.status_code, 401)

            self.login(user_id)
            self.assertEquals(current_user.get_id(), user_id)

            response = self.client.post("/blog/editor/",
                                        data=dict(text="Test Text",
                                                  tags="tag1, tag2"))
            # should give back the editor page
            self.assertEqual(response.status_code, 200)

            response = self.client.post("/blog/editor/",
                                        data=dict(title="Test Title",
                                                  text="Test Text",
                                                  tags="tag1, tag2"))
            self.assertEqual(response.status_code, 302)

            response = self.client.get("/blog/page/21/")
            self.assertEqual(response.status_code, 200)

    def test_delete(self):
        user_id = "testuser"
        with self.client:

            # Anonymous user cannot delete
            response = self.client.post("/blog/delete/1/")
            self.assertEqual(response.status_code, 401)

            # a user cannot delete another person's post
            self.login(user_id)
            self.assertEquals(current_user.get_id(), user_id)
            response = self.client.post("/blog/delete/11/",
                                        follow_redirects=True)
            assert "You do not have the rights to delete this post" in \
                   response.data

            # a user can delete his posts
            response = self.client.post("/blog/delete/1/",
                                        follow_redirects=True)
            assert "Your post was successfully deleted" in response.data

    def login(self, user_id):
        return self.client.post("/login/%s/" % user_id, follow_redirects=True)

    def logout(self):
        return self.client.get("/logout/")

    def test_sitemap(self):
        with self.client:
            # access to editor should be forbidden before login
            response = self.client.get("/blog/sitemap.xml")
            self.assertEqual(response.status_code, 200)

    def test_atom(self):
        with self.client:
            # access to editor should be forbidden before login
            response = self.client.get("/blog/feeds/all.atom.xml")
            self.assertEqual(response.status_code, 200)
