try:
    from builtins import str, range
except ImportError:
    pass
import os
import tempfile
from flask import redirect, url_for, current_app
from flask_login import LoginManager, login_user, logout_user, current_user
from sqlalchemy import create_engine, MetaData
from flask_blogging.sqlastorage import SQLAStorage
from flask_blogging import BloggingEngine
from test import FlaskBloggingTestCase, TestUser
import re
from flask_principal import identity_changed, Identity, Permission,\
    AnonymousIdentity, identity_loaded, RoleNeed, UserNeed
from flask_cache import Cache
from .utils import get_random_unicode


class TestViews(FlaskBloggingTestCase):

    def _create_storage(self):
        temp_dir = tempfile.gettempdir()
        self._dbfile = os.path.join(temp_dir, "temp.db")
        conn_string = 'sqlite:///' + self._dbfile
        engine = create_engine(conn_string)
        meta = MetaData()
        self.storage = SQLAStorage(engine, metadata=meta)
        meta.create_all(bind=engine)

    def _create_blogging_engine(self):
        return BloggingEngine(self.app, self.storage)

    def setUp(self):
        FlaskBloggingTestCase.setUp(self)
        self._create_storage()
        self.app.config["BLOGGING_URL_PREFIX"] = "/blog"
        self.app.config["BLOGGING_PLUGINS"] = []
        self.engine = self._create_blogging_engine()
        self.login_manager = LoginManager(self.app)

        @self.login_manager.user_loader
        @self.engine.user_loader
        def load_user(user_id):
            return TestUser(user_id)

        @self.app.route("/login/<username>/", methods=["POST"],
                        defaults={"blogger": 0})
        @self.app.route("/login/<username>/<int:blogger>/", methods=["POST"])
        def login(username, blogger):
            this_user = TestUser(username)
            login_user(this_user)
            if blogger:
                identity_changed.send(current_app._get_current_object(),
                                      identity=Identity(username))
            return redirect("/")

        @self.app.route("/logout/")
        def logout():
            logout_user()
            identity_changed.send(current_app._get_current_object(),
                                  identity=AnonymousIdentity())
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

        response = self.client.get("/blog/author/nonexistent_user/",
                                   follow_redirects=True)
        assert "No posts found for this user!" in str(response.data)

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
            assert "The page you are trying to access is not valid!" in \
                   str(response.data)

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

    def test_editor_edit_page(self):
        user_id = "testuser"
        with self.client:
            self.login(user_id)
            response = self.client.post(
                "/blog/editor/1/",
                data=dict(title="Sample Title0-Edited",
                          text="Sample Text0-Edited", tags="tag1, tag2"))

            response = self.client.get("/blog/100/")
            self.assertEqual(response.status_code, 200)

            pattern = re.compile(b"<h1>.*</h1>")
            headings = pattern.findall(response.data)
            self.assertEqual(len(headings), 20)
            self.assertEqual(headings[-1], b"<h1>Sample Title0-Edited</h1>")

            return

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
                   str(response.data)

            # a user can delete his posts
            response = self.client.post("/blog/delete/1/",
                                        follow_redirects=True)
            assert "Your post was successfully deleted" in str(response.data)

    def login(self, user_id, blogger=False):
        if blogger:
            return self.client.post("/login/%s/1/" % user_id,
                                    follow_redirects=True)
        else:
            return self.client.post("/login/%s/" % user_id,
                                    follow_redirects=True)

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

    def test_posts_per_page(self):
        posts_per_page = 5
        self.app.config["BLOGGING_POSTS_PER_PAGE"] = posts_per_page
        with self.client:
            pattern = re.compile(b"<h1>.*</h1>")
            # index page
            response = self.client.get("/blog/")
            headings = pattern.findall(response.data)
            self.assertEqual(len(headings), posts_per_page)

            # tag page
            response = self.client.get("/blog/tag/hello/")
            headings = pattern.findall(response.data)
            self.assertEqual(len(headings), posts_per_page)

            # author page
            response = self.client.get("/blog/author/testuser/")
            headings = pattern.findall(response.data)
            self.assertEqual(len(headings), posts_per_page)

    def test_url_construction(self):
        ctx = self.app.test_request_context()
        ctx.push()
        index_url = url_for("blogging.index")
        self.assertEqual(index_url, "/blog/")

        # index url
        index_url = url_for("blogging.index", count=10)
        self.assertEqual(index_url, "/blog/10/")

        index_url = url_for("blogging.index", count=10, page=2)
        self.assertEqual(index_url, "/blog/10/2/")

        # page by id
        page_url = url_for("blogging.page_by_id", post_id=5)
        self.assertEqual(page_url, "/blog/page/5/")

        # posts by tag
        tag_url = url_for("blogging.posts_by_tag", tag="hello")
        self.assertEqual(tag_url, "/blog/tag/hello/")

        # posts by author
        author_url = url_for("blogging.posts_by_author", user_id="newuser")
        self.assertEqual(author_url, "/blog/author/newuser/")

        # sitemap
        sitemap_url = url_for("blogging.sitemap")
        self.assertEqual(sitemap_url, "/blog/sitemap.xml")

        # feeds
        feed_url = url_for("blogging.feed")
        self.assertEqual(feed_url, "/blog/feeds/all.atom.xml")

        ctx.pop()

    def _set_identity_loader(self, role_name):
        @identity_loaded.connect_via(self.app)
        def on_identity_loaded(sender, identity):
            identity.user = current_user
            if hasattr(current_user, "id"):
                identity.provides.add(UserNeed(current_user.id))
            identity.provides.add(RoleNeed(role_name))

    def test_permissions_editor(self):
        self.app.config["BLOGGING_PERMISSIONS"] = True
        self.app.config["BLOGGING_PERMISSIONNAME"] = "testblogger"
        user_id = "newuser"
        self._set_identity_loader(self.app.config.get(
            "BLOGGING_PERMISSIONNAME", "blogger"))

        with self.client:
            response = self.client.post("/blog/editor/")
            self.assertEqual(response.status_code, 401)

            response = self.client.post("/blog/editor/1/")
            self.assertEqual(response.status_code, 401)

            self.login(user_id)
            response = self.client.post("/blog/editor/")
            self.assertEqual(response.status_code, 302)

            response = self.client.post("/blog/editor/1/")
            self.assertEqual(response.status_code, 302)

            self.logout()

            self.login(user_id, blogger=True)
            response = self.client.post("/blog/editor/")
            self.assertEqual(response.status_code, 200)

            response = self.client.post("/blog/editor/1/")
            self.assertEqual(response.status_code, 200)

            test_permission = Permission(RoleNeed("testblogger"))
            blogger_permission = Permission(RoleNeed("blogger"))
            self.assertTrue(test_permission.issubset(
                self.engine.blogger_permission))
            self.assertFalse(blogger_permission.issubset(
                self.engine.blogger_permission))

    def test_permissions_delete(self):
        self.app.config["BLOGGING_PERMISSIONS"] = True
        # Assuming "BLOGGING_PERMISSIONNAME" read failure
        # self.app.config["BLOGGING_PERMISSIONNAME"] = None
        user_id = "testuser"
        self._set_identity_loader(self.app.config.get(
            "BLOGGING_PERMISSIONNAME", "blogger"))

        with self.client:
            # Anonymous user cannot delete
            response = self.client.post("/blog/delete/1/")
            self.assertEqual(response.status_code, 401)

            self.login(user_id)
            # non blogger cannot delete posts
            response = self.client.post("/blog/delete/1/")
            self.assertEqual(response.status_code, 302)  # will be redirected
            self.logout()

            self.login(user_id, blogger=True)
            response = self.client.post("/blog/delete/1/",
                                        follow_redirects=True)
            assert "Your post was successfully deleted" in str(response.data)

            # a user cannot delete another person's post
            self.assertEquals(current_user.get_id(), user_id)
            response = self.client.post("/blog/delete/11/",
                                        follow_redirects=True)
            assert "You do not have the rights to delete this post" in \
                   str(response.data)

            test_permission = Permission(RoleNeed("testblogger"))
            blogger_permission = Permission(RoleNeed("blogger"))
            self.assertFalse(test_permission.issubset(
                self.engine.blogger_permission))
            self.assertTrue(blogger_permission.issubset(
                self.engine.blogger_permission))


class TestViewsWithCache(TestViews):

    def _create_blogging_engine(self):
        cache = Cache(self.app, config={"CACHE_TYPE": "simple"})
        return BloggingEngine(self.app, self.storage, cache=cache)


class TestViewsWithUnicode(TestViews):

    def setUp(self):
        TestViews.setUp(self)

        for i in range(20):
            tags = ["unicode hello"] if i < 10 else ["unicode world"]
            user = "testuser" if i < 10 else "newuser"
            self.storage.save_post(
                title=u'{0}_{1}'.format(get_random_unicode(15), i),
                text=u'{0}_{1}'.format(get_random_unicode(200), i),
                user_id=user, tags=tags)

    def test_editor_edit_page(self):
        pass

    def test_editor_post(self):
        pass
