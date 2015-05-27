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
            expected_columns = ['id', 'title', 'text', 'post_date', 'last_modified_date', 'user_id', 'draft']
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

    #def test_tablename_with_prefix(self):
    #    prefix = "blog_data_"
