__author__ = 'Gouthaman Balaraman'


from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import logging

#from flask.ext.sqlalchemy import SQLAlchemy
#db = SQLAlchemy()



class SQLAStorage(object):

    def __init__(self, app):
        #global db
        #db.init_app(app)
        pass


"""
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    text = db.Column(db.Text)
    post_date = db.Column(db.DateTime)
    modified_date = db.Column(db.DateTime)

Base = declarative_base()
"""





import sqlalchemy as sqla
class SQLAStorage(object):
    _db = None
    _logger = logging.getLogger("flask-blogging")

    def __init__(self, db, table_prefix=""):
        self._engine = db.engine
        self._table_prefix = table_prefix
        self._create_all_tables()

    def _table_name(self, table_name):
        return self._table_prefix+table_name

    def _create_all_tables(self):
        self._create_post_table()
        self._create_tag_table()
        self._create_tag_posts_table()
        self._create_user_posts_table()

    def _create_post_table(self):
        with self._engine.begin() as conn:
            metadata = sqla.MetaData()
            post_table_name = self._table_name("post")
            if not conn.dialect.has_table(conn, post_table_name ):
                self._post_table = sqla.Table(
                    post_table_name, metadata,
                    sqla.Column("id", sqla.Integer, primary_key=True),
                    sqla.Column("title", sqla.String(256)),
                    sqla.Column("text", sqla.Text),
                    sqla.Column("post_date", sqla.DateTime),
                    sqla.Column("last_modified_date", sqla.DateTime),
                    sqla.Column("user_id", sqla.Integer),
                    sqla.Column("draft", sqla.SmallInteger, default=0)  # if 1 then make it a draft an
                )
                metadata.create_all(self._engine)
                self._logger.debug("Created table with table name %s" % post_table_name)
            else:
                metadata.reflect(bind=self._engine)
                self._post_table = metadata.tables[post_table_name]
                self._logger.debug("Reflecting to table with table name %s" % post_table_name)

    def _create_tag_table(self):
        with self._engine.begin() as conn:
            metadata = sqla.MetaData()
            tag_table_name = self._table_name("tag")
            if not conn.dialect.has_table(conn, tag_table_name ):
                self._tag_table = sqla.Table(
                    tag_table_name, metadata,
                    sqla.Column("id", sqla.Integer, primary_key=True),
                    sqla.Column("text", sqla.String(128), unique=True)
                )
                metadata.create_all(self._engine)
                self._logger.debug("Created table with table name %s" % tag_table_name)
            else:
                metadata.reflect(bind=self._engine)
                self._tag_table = metadata.tables[tag_table_name]
                self._logger.debug("Reflecting to table with table name %s" % tag_table_name)

    def _create_tag_posts_table(self):
        with self._engine.begin() as conn:
            metadata = sqla.MetaData()
            tag_posts_table_name = self._table_name("tag_posts")
            if not conn.dialect.has_table(conn, tag_posts_table_name ):
                tag_id = self._table_name("tag")+".id"
                post_id = self._table_name("post")+".id"
                self._tag_posts_table = sqla.Table(
                    tag_posts_table_name, metadata,
                    sqla.Column('tag_id', sqla.Integer, index=True),
                    sqla.Column('post_id', sqla.Integer, index=True)
                    )
                metadata.create_all(self._engine)
                self._logger.debug("Created table with table name %s" % tag_posts_table_name)
            else:
                metadata.reflect(bind=self._engine)
                self._tag_posts_table = metadata.tables[tag_posts_table_name]
                self._logger.debug("Reflecting to table with table name %s" % tag_posts_table_name)

    def _create_user_posts_table(self):
        with self._engine.begin() as conn:
            metadata = sqla.MetaData()
            user_posts_table_name = self._table_name("user_posts")
            if not conn.dialect.has_table(conn, user_posts_table_name ):
                post_id = self._table_name("post")+".id"
                self._user_posts_table = sqla.Table(
                    user_posts_table_name, metadata,
                    sqla.Column("user_id", sqla.Integer, index=True),
                    sqla.Column("post_id", sqla.Integer, index=True)
                )
                metadata.create_all(self._engine)
                self._logger.debug("Created table with table name %s" % user_posts_table_name)
            else:
                metadata.reflect(bind=self._engine)
                self._user_posts_table = metadata.tables[user_posts_table_name]
                self._logger.debug("Reflecting to table with table name %s" % user_posts_table_name)