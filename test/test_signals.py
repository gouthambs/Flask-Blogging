import os
from flask import current_app, redirect
from test import FlaskBloggingTestCase, TestUser
import tempfile
from sqlalchemy import create_engine, MetaData
from flask_blogging import SQLAStorage, BloggingEngine
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_principal import identity_changed, Identity, \
    AnonymousIdentity, identity_loaded, RoleNeed, UserNeed
from test.plugin import disconnect_receivers


class SignalCountingBloggingEngine(BloggingEngine):
    ctr_blueprint_created = 0
    ctr_sitemap_posts = 0
    ctr_feed_posts_fetched = 0
    ctr_feed_posts_processed = 0
    ctr_index_posts = 0
    ctr_page_by_id = 0
    ctr_posts_by_tag = 0
    ctr_posts_by_author = 0


class TestSignals(FlaskBloggingTestCase):

    def _create_storage(self):
        temp_dir = tempfile.gettempdir()
        self._dbfile = os.path.join(temp_dir, "temp.db")
        conn_string = 'sqlite:///'+self._dbfile
        engine = create_engine(conn_string)
        meta = MetaData()
        self.storage = SQLAStorage(engine, metadata=meta)
        meta.create_all(bind=engine)

    def _create_blogging_engine(self):
        return SignalCountingBloggingEngine(self.app, self.storage)

    def tearDown(self):
        disconnect_receivers(self.app)

    def setUp(self):
        FlaskBloggingTestCase.setUp(self)
        self._create_storage()
        self.app.config["BLOGGING_URL_PREFIX"] = "/blog"
        self.app.config["BLOGGING_PLUGINS"] = ["test.plugin"]
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

    def test_blueprint_created_signal(self):
        with self.client:
            self.assertEqual(self.engine.ctr_blueprint_created, 1)

    def test_sitemap_signals(self):
        with self.client:
            response = self.client.get("/blog/sitemap.xml")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.engine.ctr_sitemap_posts, 2)

    def test_feed_signals(self):
        with self.client:
            response = self.client.get("/blog/feeds/all.atom.xml")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.engine.ctr_feed_posts_fetched, 1)
            self.assertEqual(self.engine.ctr_feed_posts_processed, 1)

    def test_index_posts_signals(self):
        with self.client:
            response = self.client.get("/blog/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.engine.ctr_index_posts, 2)

    def test_page_by_id_signals(self):
        with self.client:
            response = self.client.get("/blog/page/1/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.engine.ctr_page_by_id, 2)

    def test_posts_by_tag_signals(self):
        with self.client:
            response = self.client.get("/blog/tag/hello/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.engine.ctr_posts_by_tag, 2)

    def test_posts_by_author_signals(self):
        with self.client:
            response = self.client.get("/blog/author/testuser/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.engine.ctr_posts_by_author, 2)
