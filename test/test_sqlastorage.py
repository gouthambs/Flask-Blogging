__author__ = 'gbalaraman'

import tempfile
import os
from flask_blogging.sqlastorage import SQLAStorage
from sqlalchemy import create_engine
from test import FlaskBloggingTestCase
import sqlalchemy as sqla

class TestSQLiteStorage(FlaskBloggingTestCase):

    def _create_storage(self):
        temp_dir = tempfile.gettempdir()
        self._dbfile = os.path.join(temp_dir, "temp.db")
        self._engine = create_engine('sqlite:///'+self._dbfile)
        self.storage = SQLAStorage(self._engine)

    def setUp(self):
        FlaskBloggingTestCase.setUp(self)
        self._create_storage()

    def tearDown(self):
        os.remove(self._dbfile)

    def test_post_table_exists(self):
        table_name = "post"
        with self._engine.begin() as conn:
            self.assertTrue(conn.dialect.has_table(conn, table_name))
            metadata = sqla.MetaData()
            metadata.reflect(bind=self._engine)
            table = metadata.tables[table_name]
            columns = [t.name for t in table.columns]
            expected_columns = ['id', 'title', 'text', 'post_date', 'last_modified_date', 'draft']
            self.assertListEqual(columns, expected_columns)

    def test_tag_table_exists(self):
        table_name = "tag"
        with self._engine.begin() as conn:
            self.assertTrue(conn.dialect.has_table(conn, table_name))
            metadata = sqla.MetaData()
            metadata.reflect(bind=self._engine)
            table = metadata.tables[table_name]
            columns = [t.name for t in table.columns]
            expected_columns = ['id', 'text']
            self.assertListEqual(columns, expected_columns)

    def test_tag_post_table_exists(self):
        table_name = "tag_posts"
        with self._engine.begin() as conn:
            self.assertTrue(conn.dialect.has_table(conn, table_name))
            metadata = sqla.MetaData()
            metadata.reflect(bind=self._engine)
            table = metadata.tables[table_name]
            columns = [t.name for t in table.columns]
            expected_columns = ['tag_id', 'post_id']
            self.assertListEqual(columns, expected_columns)

    def test_user_post_table_exists(self):
        table_name = "user_posts"
        with self._engine.begin() as conn:
            self.assertTrue(conn.dialect.has_table(conn, table_name))
            metadata = sqla.MetaData()
            metadata.reflect(bind=self._engine)
            table = metadata.tables[table_name]
            columns = [t.name for t in table.columns]
            expected_columns = ['user_id', 'post_id']
            self.assertListEqual(columns, expected_columns)

    def test_user_post_table_consistency(self):
        # check if the user post table updates the user_id
        user_id = 1; post_id = 5
        with self._engine.begin() as conn:
            self.storage._save_user_post(user_id, post_id, conn)
            statement = sqla.select([self.storage._user_posts_table])
            result = conn.execute(statement).fetchall()
            self.assertEqual(len(result), 1)
            self.assertListEqual(result, [('1', 5)])

            self.storage._save_user_post(user_id+4, post_id, conn)
            statement = sqla.select([self.storage._user_posts_table])
            result = conn.execute(statement).fetchall()
            self.assertEqual(len(result), 1)
            self.assertListEqual(result, [('5', 5)])
        return

    def test_tags_uniqueness(self):
        table_name = "tag"
        metadata = sqla.MetaData()
        metadata.reflect(bind=self._engine)
        table = metadata.tables[table_name]
        with self._engine.begin() as conn:
            statement = table.insert().values(text="test_tag")
            conn.execute(statement)
        # reentering same tag should raise exception
        with self._engine.begin() as conn:
            statement = table.insert().values(text="test_tag")
            self.assertRaises(sqla.exc.IntegrityError, conn.execute, statement)

    def test_tags_consistency(self):
        tags = ["hello", "world"]
        post_id = 2
        with self._engine.begin() as conn:
            self.storage._save_tags(tags, post_id, conn)
            statement = sqla.select([self.storage._tag_posts_table]).\
                where(self.storage._tag_posts_table.c.post_id==post_id)
            result = conn.execute(statement).fetchall()
            self.assertEqual(len(result), 2)

            tags.pop()
            self.storage._save_tags(tags, post_id, conn)
            statement = sqla.select([self.storage._tag_posts_table]).\
                where(self.storage._tag_posts_table.c.post_id==post_id)
            result = conn.execute(statement).fetchall()
            self.assertEqual(len(result), 1)

    def test_tag_post_uniqueness(self):
        table_name = "tag_posts"
        metadata = sqla.MetaData()
        metadata.reflect(bind=self._engine)
        table = metadata.tables[table_name]
        with self._engine.begin() as conn:
            statement = table.insert().values(tag_id=1, post_id=1)
            conn.execute(statement)
        # reentering same tag should raise exception
        with self._engine.begin() as conn:
            statement = table.insert().values(tag_id=1, post_id=1)
            self.assertRaises(sqla.exc.IntegrityError, conn.execute, statement)

    def test_user_post_uniqueness(self):
        table_name = "user_posts"
        metadata = sqla.MetaData()
        metadata.reflect(bind=self._engine)
        table = metadata.tables[table_name]
        with self._engine.begin() as conn:
            statement = table.insert().values(user_id=1, post_id=1)
            conn.execute(statement)
        # reentering same tag should raise exception
        with self._engine.begin() as conn:
            statement = table.insert().values(user_id=1, post_id=1)
            self.assertRaises(sqla.exc.IntegrityError, conn.execute, statement)

    def test_bind_database(self):
        self.storage._create_all_tables()
        self.test_post_table_exists()
        self.test_tag_table_exists()
        self.test_tag_post_table_exists()
        self.test_user_post_table_exists()

    def test_save_post(self):
        pid = self.storage.save_post(title="Title1", text="Sample Text", user_id="testuser",tags=["hello", "world"])
        pid = self.storage.save_post(title="Title1", text="Sample Text", user_id="testuser",tags=["hello", "world"], post_id=1)
        p = self.storage.get_post_by_id(2)
        self.assertIsNone(p)

        # invalid post_id will be treated as inserts
        pid = self.storage.save_post(title="Title1", text="Sample Text", user_id="testuser",tags=["hello", "world"],
                                     post_id=5)
        self.assertNotEqual(pid, 5)
        self.assertEqual(pid, 2)
        p = self.storage.get_post_by_id(2)
        self.assertIsNotNone(p)

    def test_delete_post(self):
        # insert, check exists, delete, check doesn't exist anymore
        pid = self.storage.save_post(title="Title1", text="Sample Text", user_id="testuser",tags=["hello", "world"])
        p = self.storage.get_post_by_id(pid)
        self.assertIsNotNone(p)
        self.storage.delete_post(pid)
        p = self.storage.get_post_by_id(pid)
        self.assertIsNone(p)

        # insert again.
        pid = self.storage.save_post(title="Title1", text="Sample Text", user_id="testuser",tags=["hello", "world"],
                                     post_id=1)
        p = self.storage.get_post_by_id(pid)
        self.assertIsNotNone(p)

    def test_get_post_by_id(self):
        pid1 = self.storage.save_post(title="Title1", text="Sample Text1", user_id="testuser", tags=["hello", "world"])
        pid2 = self.storage.save_post(title="Title2", text="Sample Text2", user_id="testuser",
                                      tags=["hello", "my", "world"])

        post = self.storage.get_post_by_id(pid1)
        self._assert_post(post, "Title1", "Sample Text1", "testuser", ["HELLO", "WORLD"])

        post = self.storage.get_post_by_id(pid2)
        self._assert_post(post, "Title2", "Sample Text2", "testuser", ["HELLO", "MY", "WORLD"])

    def _assert_post(self, post, title, text, user_id, tags):
        tags = set([t.upper() for t in tags])
        self.assertSetEqual(set(post["tags"]), tags)
        self.assertEqual(post["title"], title)
        self.assertEqual(post["text"], text)
        self.assertEqual(post["user_id"], user_id)

    def test_get_posts(self):
        for i in range(20):
            tags = ["hello"] if i < 10 else ["world"]
            user = "testuser" if i<10 else "newuser"
            self.storage.save_post(title="Title%d" % i, text="Sample Text%d" % i, user_id=user,tags=tags)
        # test default queries
        posts = self.storage.get_posts()
        self.assertEqual(len(posts), 10)
        ctr = 19
        for post in posts:
            self._assert_post(post, "Title%d" % ctr, "Sample Text%d" % ctr, "newuser", ["world"])
            ctr -= 1

        posts = self.storage.get_posts(recent=False)
        self.assertEqual(len(posts), 10)
        ctr = 0
        for post in posts:
            self._assert_post(post, "Title%d" % ctr, "Sample Text%d" % ctr, "testuser", ["hello"])
            ctr += 1

        # test count and offset
        posts = self.storage.get_posts(count=5, offset=5, recent=False)
        self.assertEqual(len(posts), 5)
        ctr = 5
        for post in posts:
            self._assert_post(post, "Title%d" % ctr, "Sample Text%d" % ctr, "testuser", ["hello"])
            ctr += 1

        # test tag feature
        posts = self.storage.get_posts(tag="hello", recent=False)
        self.assertEqual(len(posts), 10)
        ctr = 0
        for post in posts:
            self._assert_post(post, "Title%d" % ctr, "Sample Text%d" % ctr, "testuser", ["hello"])
            ctr += 1
        posts = self.storage.get_posts(tag="world", recent=False)
        self.assertEqual(len(posts), 10)
        ctr = 10
        for post in posts:
            self._assert_post(post, "Title%d" % ctr, "Sample Text%d" % ctr, "newuser", ["world"])
            ctr += 1

        # test user_id feature
        posts = self.storage.get_posts(user_id="newuser", recent=True)
        self.assertEqual(len(posts), 10)
        ctr = 19
        for post in posts:
            self._assert_post(post, "Title%d" % ctr, "Sample Text%d" % ctr, "newuser", ["world"])
            ctr -= 1

        posts = self.storage.get_posts(user_id="testuser", recent=True)
        self.assertEqual(len(posts), 10)
        ctr = 9
        for post in posts:
            self._assert_post(post, "Title%d" % ctr, "Sample Text%d" % ctr, "testuser", ["hello"])
            ctr -= 1
        return

    def test_count_posts(self):
        for i in range(20):
            tags = ["hello"] if i < 10 else ["world"]
            user = "testuser" if i<10 else "newuser"
            self.storage.save_post(title="Title%d" % i, text="Sample Text%d" % i, user_id=user,tags=tags)

        count = self.storage.count_posts()
        self.assertEqual(count, 20)

        # test user
        count = self.storage.count_posts(user_id="testuser")
        self.assertEqual(count, 10)

        count = self.storage.count_posts(user_id="newuser")
        self.assertEqual(count, 10)

        count = self.storage.count_posts(user_id="testuser")
        self.assertEqual(count, 10)

        # test tags
        count = self.storage.count_posts(tag="hello")
        self.assertEqual(count, 10)

        count = self.storage.count_posts(tag="world")
        self.assertEqual(count, 10)

        # multiple queries
        count = self.storage.count_posts(user_id="testuser", tag="world")
        self.assertEqual(count, 0)