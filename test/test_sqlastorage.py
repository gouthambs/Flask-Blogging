__author__ = 'gbalaraman'

import tempfile
import os
from flask_blogging.sqlastorage import SQLAStorage
from flask.ext.sqlalchemy import SQLAlchemy
from test import FlaskBloggingTestCase
import sqlalchemy as sqla

class TestSQLiteStorage(FlaskBloggingTestCase):

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

    def tearDown(self):
        os.remove(self._dbfile)

    def test_post_table_exists(self):
        table_name = "post"
        with self._db.engine.begin() as conn:
            self.assertTrue(conn.dialect.has_table(conn, table_name))
            metadata = sqla.MetaData()
            metadata.reflect(bind=self._db.engine)
            table = metadata.tables[table_name]
            columns = [t.name for t in table.columns]
            expected_columns = ['id', 'title', 'text', 'post_date', 'last_modified_date', 'draft']
            self.assertListEqual(columns, expected_columns)

    def test_tag_table_exists(self):
        table_name = "tag"
        with self._db.engine.begin() as conn:
            self.assertTrue(conn.dialect.has_table(conn, table_name))
            metadata = sqla.MetaData()
            metadata.reflect(bind=self._db.engine)
            table = metadata.tables[table_name]
            columns = [t.name for t in table.columns]
            expected_columns = ['id', 'text']
            self.assertListEqual(columns, expected_columns)

    def test_tag_post_table_exists(self):
        table_name = "tag_posts"
        with self._db.engine.begin() as conn:
            self.assertTrue(conn.dialect.has_table(conn, table_name))
            metadata = sqla.MetaData()
            metadata.reflect(bind=self._db.engine)
            table = metadata.tables[table_name]
            columns = [t.name for t in table.columns]
            expected_columns = ['tag_id', 'post_id']
            self.assertListEqual(columns, expected_columns)

    def test_user_post_table_exists(self):
        table_name = "user_posts"
        with self._db.engine.begin() as conn:
            self.assertTrue(conn.dialect.has_table(conn, table_name))
            metadata = sqla.MetaData()
            metadata.reflect(bind=self._db.engine)
            table = metadata.tables[table_name]
            columns = [t.name for t in table.columns]
            expected_columns = ['user_id', 'post_id']
            self.assertListEqual(columns, expected_columns)

    def test_tags_uniqueness(self):
        table_name = "tag"
        metadata = sqla.MetaData()
        metadata.reflect(bind=self._db.engine)
        table = metadata.tables[table_name]
        with self._db.engine.begin() as conn:
            statement = table.insert().values(text="test_tag")
            conn.execute(statement)
        # reentering same tag should raise exception
        with self._db.engine.begin() as conn:
            statement = table.insert().values(text="test_tag")
            self.assertRaises(sqla.exc.IntegrityError, conn.execute, statement)

    def test_tag_post_uniqueness(self):
        table_name = "tag_posts"
        metadata = sqla.MetaData()
        metadata.reflect(bind=self._db.engine)
        table = metadata.tables[table_name]
        with self._db.engine.begin() as conn:
            statement = table.insert().values(tag_id=1, post_id=1)
            conn.execute(statement)
        # reentering same tag should raise exception
        with self._db.engine.begin() as conn:
            statement = table.insert().values(tag_id=1, post_id=1)
            self.assertRaises(sqla.exc.IntegrityError, conn.execute, statement)

    def test_user_post_uniqueness(self):
        table_name = "user_posts"
        metadata = sqla.MetaData()
        metadata.reflect(bind=self._db.engine)
        table = metadata.tables[table_name]
        with self._db.engine.begin() as conn:
            statement = table.insert().values(user_id=1, post_id=1)
            conn.execute(statement)
        # reentering same tag should raise exception
        with self._db.engine.begin() as conn:
            statement = table.insert().values(user_id=1, post_id=1)
            self.assertRaises(sqla.exc.IntegrityError, conn.execute, statement)

    def test_bind_database(self):
        self.storage._create_all_tables()
        self.test_post_table_exists()
        self.test_tag_table_exists()
        self.test_tag_post_table_exists()
        self.test_user_post_table_exists()

    def test_save_post(self):
        self.storage.save_post(title="title", text="Sample Text", user_id="testuser",tags=["hello", "world"])
        self.storage.save_post(title="title", text="Sample Text", user_id="testuser",tags=["hello", "world"],post_id=1)

    def test_get_post_by_id(self):
        self.storage.save_post(title="title", text="Sample Text", user_id="testuser",tags=["hello", "world"])
        self.storage.get_post_by_id(1)