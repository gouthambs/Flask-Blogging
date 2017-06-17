try:
    from builtins import str
except ImportError:
    pass
import sys
import logging
import sqlalchemy as sqla
from sqlalchemy.ext.automap import automap_base
import datetime
from .storage import Storage
from .signals import sqla_initialized

this = sys.modules[__name__]
this.Post = None
this.Tag = None


class SQLAStorage(Storage):
    """
    The ``SQLAStorage`` implements the interface specified by the ``Storage``
    class. This  class uses SQLAlchemy to implement storage and retrieval of
    data from any of the databases supported by SQLAlchemy.
    """
    _db = None
    _logger = logging.getLogger("flask-blogging")

    def __init__(self, engine=None, table_prefix="", metadata=None, db=None,
                 bind=None):
        """
        The constructor for the ``SQLAStorage`` class.

        :param engine: The ``SQLAlchemy`` engine instance created by calling
        ``create_engine``. One can also use Flask-SQLAlchemy, and pass the
        engine property.
        :type engine: object
        :param table_prefix: (Optional) Prefix to use for the tables created
         (default ``""``).
        :type table_prefix: str
        :param metadata: (Optional) The SQLAlchemy MetaData object
        :type metadata: object
        :param db: (Optional) The Flask-SQLAlchemy SQLAlchemy object
        :type db: object
        :param bind: (Optional) Reference the database to bind for multiple
        database scenario with binds
        :type bind: str
        """
        self._bind = bind
        if db:
            self._engine = db.get_engine(db.get_app(), bind=self._bind)
            self._metadata = db.metadata
        else:
            if engine is None:
                raise ValueError("Both db and engine args cannot be None")
            self._engine = engine
            self._metadata = metadata or sqla.MetaData()
        self._info = {} if self._bind is None else {"bind_key": self._bind}
        self._table_prefix = table_prefix
        table_suffix = ['post', 'tag', 'user_posts', 'tag_posts']
        tables = [self._table_name(t) for t in table_suffix]
        self._metadata.reflect(bind=self._engine)
        self._create_all_tables()
        self._Base = automap_base(metadata=self._metadata)
        self._Base.prepare()
        self._inject_models()
        sqla_initialized.send(self, engine=self._engine,
                              table_prefix=self._table_prefix,
                              meta=self.metadata,
                              bind=self._bind)

    def _inject_models(self):
        global this
        this.Post = getattr(self._Base.classes, self._table_name("post"))
        this.Tag = getattr(self._Base.classes, self._table_name("tag"))

    @property
    def metadata(self):
        return self._metadata

    @property
    def post_table(self):
        return self._post_table

    @property
    def post_model(self):
        return getattr(self._Base.classes, self._table_name("post"))

    @property
    def tag_model(self):
        return getattr(self._Base.classes, self._table_name("tag"))

    @property
    def tag_table(self):
        return self._tag_table

    @property
    def tag_posts_table(self):
        return self._tag_posts_table

    @property
    def user_posts_table(self):
        return self._user_posts_table

    @property
    def engine(self):
        return self._engine

    def save_post(self, title, text, user_id, tags, draft=False,
                  post_date=None, last_modified_date=None, meta_data=None,
                  post_id=None):
        """
        Persist the blog post data. If ``post_id`` is ``None`` or ``post_id``
        is invalid, the post must be inserted into the storage. If ``post_id``
        is a valid id, then the data must be updated.

        :param title: The title of the blog post
        :type title: str
        :param text: The text of the blog post
        :type text: str
        :param user_id: The user identifier
        :type user_id: str
        :param tags: A list of tags
        :type tags: list
        :param draft: (Optional) If the post is a draft of if needs to be
         published. (default ``False``)
        :type draft: bool
        :param post_date: (Optional) The date the blog was posted (default
         datetime.datetime.utcnow() )
        :type post_date: datetime.datetime
        :param last_modified_date: (Optional) The date when blog was last
         modified  (default datetime.datetime.utcnow() )
        :type last_modified_date: datetime.datetime
        :param post_id: (Optional) The post identifier. This should be ``None``
         for an insert call,
         and a valid value for update. (default ``None``)
        :type post_id: int

        :return: The post_id value, in case of a successful insert or update.
         Return ``None`` if there were errors.
        """
        new_post = post_id is None
        current_datetime = datetime.datetime.utcnow()
        draft = 1 if draft is True else 0
        post_date = post_date if post_date is not None else current_datetime
        last_modified_date = last_modified_date if last_modified_date is not \
            None else current_datetime

        with self._engine.begin() as conn:
            try:
                if post_id is not None:  # validate post_id
                    exists_statement = sqla.select([self._post_table]).where(
                        self._post_table.c.id == post_id)
                    exists = \
                        conn.execute(exists_statement).fetchone() is not None
                    post_id = post_id if exists else None
                post_statement = \
                    self._post_table.insert() if post_id is None else \
                    self._post_table.update().where(
                        self._post_table.c.id == post_id)
                post_statement = post_statement.values(
                    title=title, text=text, post_date=post_date,
                    last_modified_date=last_modified_date, draft=draft
                )

                post_result = conn.execute(post_statement)
                post_id = post_result.inserted_primary_key[0] \
                    if post_id is None else post_id
                self._save_tags(tags, post_id, conn)
                self._save_user_post(user_id, post_id, conn)

            except Exception as e:
                self._logger.exception(str(e))
                post_id = None
        return post_id

    def get_post_by_id(self, post_id):
        """
        Fetch the blog post given by ``post_id``

        :param post_id: The post identifier for the blog post
        :type post_id: int
        :return: If the ``post_id`` is valid, the post data is retrieved, else
         returns ``None``.
        """
        r = None
        with self._engine.begin() as conn:
            try:
                post_statement = sqla.select([self._post_table]).where(
                    self._post_table.c.id == post_id
                )
                post_result = conn.execute(post_statement).fetchone()
                if post_result is not None:
                    r = dict(post_id=post_result[0], title=post_result[1],
                             text=post_result[2], post_date=post_result[3],
                             last_modified_date=post_result[4],
                             draft=post_result[5])
                    # get the tags
                    tag_statement = sqla.select([self._tag_table.c.text]). \
                        where(
                            sqla.and_(
                                self._tag_table.c.id ==
                                self._tag_posts_table.c.tag_id,
                                self._tag_posts_table.c.post_id == post_id))
                    tag_result = conn.execute(tag_statement).fetchall()
                    r["tags"] = [t[0] for t in tag_result]
                    # get the user
                    user_statement = sqla.select([
                        self._user_posts_table.c.user_id]).where(
                        self._user_posts_table.c.post_id == post_id
                    )
                    user_result = conn.execute(user_statement).fetchone()
                    r["user_id"] = user_result[0]
            except Exception as e:
                self._logger.exception(str(e))
                r = None
        return r

    def get_posts(self, count=10, offset=0, recent=True, tag=None,
                  user_id=None, include_draft=False):
        """
        Get posts given by filter criteria

        :param count: The number of posts to retrieve (default 10)
        :type count: int
        :param offset: The number of posts to offset (default 0)
        :type offset: int
        :param recent: Order by recent posts or not
        :type recent: bool
        :param tag: Filter by a specific tag
        :type tag: str
        :param user_id: Filter by a specific user
        :type user_id: str
        :param include_draft: Whether to include posts marked as draft or not
        :type include_draft: bool

        :return: A list of posts, with each element a dict containing values
         for the following keys: (title, text, draft, post_date,
         last_modified_date). If count is ``None``, then all the posts are
         returned.
        """
        ordering = sqla.desc(self._post_table.c.post_date) if recent \
            else self._post_table.c.post_date
        user_id = str(user_id) if user_id else user_id

        with self._engine.begin() as conn:
            try:
                select_statement = sqla.select([self._post_table.c.id])
                sql_filter = self._get_filter(tag, user_id, include_draft,
                                              conn)

                if sql_filter is not None:
                    select_statement = select_statement.where(sql_filter)
                if count:
                    select_statement = select_statement.limit(count)
                if offset:
                    select_statement = select_statement.offset(offset)

                select_statement = select_statement.order_by(ordering)
                result = conn.execute(select_statement).fetchall()
            except Exception as e:
                self._logger.exception(str(e))
                result = []

        posts = [self.get_post_by_id(pid[0]) for pid in result]
        return posts

    def count_posts(self, tag=None, user_id=None, include_draft=False):
        """
        Returns the total number of posts for the give filter

        :param tag: Filter by a specific tag
        :type tag: str
        :param user_id: Filter by a specific user
        :type user_id: str
        :param include_draft: Whether to include posts marked as draft or not
        :type include_draft: bool
        :return: The number of posts for the given filter.
        """
        result = 0
        with self._engine.begin() as conn:
            try:
                count_statement = sqla.select([sqla.func.count()]). \
                    select_from(self._post_table)
                sql_filter = self._get_filter(tag, user_id, include_draft,
                                              conn)
                count_statement = count_statement.where(sql_filter)
                result = conn.execute(count_statement).scalar()
            except Exception as e:
                self._logger.exception(str(e))
                result = 0
        return result

    def delete_post(self, post_id):
        """
        Delete the post defined by ``post_id``

        :param post_id: The identifier corresponding to a post
        :type post_id: int
        :return: Returns True if the post was successfully deleted and False
         otherwise.
        """
        status = False
        success = 0
        with self._engine.begin() as conn:
            try:
                post_del_statement = self._post_table.delete().where(
                    self._post_table.c.id == post_id)
                conn.execute(post_del_statement)
                success += 1
            except Exception as e:
                self._logger.exception(str(e))
            try:
                user_posts_del_statement = self._user_posts_table.delete(). \
                    where(self._user_posts_table.c.post_id == post_id)
                conn.execute(user_posts_del_statement)
                success += 1
            except Exception as e:
                self._logger.exception(str(e))
            try:
                tag_posts_del_statement = self._tag_posts_table.delete(). \
                    where(self._tag_posts_table.c.post_id == post_id)
                conn.execute(tag_posts_del_statement)
                success += 1
            except Exception as e:
                self._logger.exception(str(e))
        status = success == 3
        return status

    def _get_filter(self, tag, user_id, include_draft, conn):
        filters = []
        if tag:
            tag = tag.upper()
            tag_statement = sqla.select([self._tag_table.c.id]).where(
                self._tag_table.c.text == tag)
            tag_result = conn.execute(tag_statement).fetchone()
            if tag_result is not None:
                tag_id = tag_result[0]
                tag_filter = sqla.and_(
                    self._tag_posts_table.c.tag_id == tag_id,
                    self._post_table.c.id == self._tag_posts_table.c.post_id
                )
                filters.append(tag_filter)

        if user_id:
            user_filter = sqla.and_(
                self._user_posts_table.c.user_id == user_id,
                self._post_table.c.id == self._user_posts_table.c.post_id
            )
            filters.append(user_filter)

        draft_filter = self._post_table.c.draft == 1 if include_draft else \
            self._post_table.c.draft == 0
        filters.append(draft_filter)
        sql_filter = sqla.and_(*filters)
        return sql_filter

    def _save_tags(self, tags, post_id, conn):

        tags = self.normalize_tags(tags)
        tag_ids = []

        for tag in tags:  # iterate over given tags
            try:
                # check if the tag exists
                statement = self._tag_table.select().where(
                    self._tag_table.c.text == tag)
                tag_result = conn.execute(statement).fetchone()
                if tag_result is None:
                    # insert if it is a new tag
                    tag_insert_statement = self._tag_table.insert().\
                        values(text=tag)
                    result = conn.execute(tag_insert_statement)
                    tag_id = result.inserted_primary_key[0]
                else:
                    # tag already exists
                    tag_id = tag_result[0]

            except sqla.exc.IntegrityError as e:
                # some database error occurred;
                tag_id = None
                self._logger.exception(str(e))

            except Exception as e:
                # unknown exception occurred
                tag_id = None
                self._logger.exception(str(e))

            if tag_id is not None:
                # for a valid tag_id
                tag_ids.append(tag_id)

                try:
                    # check if given post has tag given by tag_id
                    statement = self._tag_posts_table.select().where(
                        sqla.and_(self._tag_posts_table.c.tag_id == tag_id,
                                  self._tag_posts_table.c.post_id == post_id))
                    tag_post_result = conn.execute(statement).fetchone()

                    if tag_post_result is None:
                        # if tag_id not present for the post given by post_id
                        tag_post_statement = self._tag_posts_table.insert().\
                            values(tag_id=tag_id, post_id=post_id)
                        conn.execute(tag_post_statement)

                except sqla.exc.IntegrityError as e:
                    self._logger.exception(str(e))
                except Exception as e:
                    self._logger.exception(str(e))
        try:
            # remove tags that have been deleted
            statement = self._tag_posts_table.delete().where(
                sqla.and_(sqla.not_(
                    self._tag_posts_table.c.tag_id.in_(tag_ids)),
                    self._tag_posts_table.c.post_id == post_id
                )
            )
            conn.execute(statement)
        except Exception as e:
            self._logger.exception(str(e))

    def _save_user_post(self, user_id, post_id, conn):
        user_id = str(user_id)
        statement = sqla.select([self._user_posts_table]).where(
            self._user_posts_table.c.post_id == post_id)
        result = conn.execute(statement).fetchone()
        if result is None:
            try:
                statement = self._user_posts_table.insert().values(
                    user_id=user_id, post_id=post_id)
                conn.execute(statement)
            except Exception as e:
                self._logger.exception(str(e))
        else:
            if result[0] != user_id:
                try:
                    statement = self._user_posts_table.update().where(
                        self._user_posts_table.c.post_id == post_id). \
                        values(user_id=user_id)
                    conn.execute(statement)
                except Exception as e:
                    self._logger.exception(str(e))

    def _table_name(self, table_name):
        return self._table_prefix + table_name

    def _create_all_tables(self):
        """
        Creates all the required tables by calling the required functions.
        :return:
        """
        self._create_post_table()
        self._create_tag_table()
        self._create_tag_posts_table()
        self._create_user_posts_table()

    def _create_post_table(self):
        """
        Creates the table to store the blog posts.
        :return:
        """
        with self._engine.begin() as conn:
            post_table_name = self._table_name("post")
            if not conn.dialect.has_table(conn, post_table_name):

                self._post_table = sqla.Table(
                    post_table_name, self._metadata,
                    sqla.Column("id", sqla.Integer, primary_key=True),
                    sqla.Column("title", sqla.String(256)),
                    sqla.Column("text", sqla.Text),
                    sqla.Column("post_date", sqla.DateTime),
                    sqla.Column("last_modified_date", sqla.DateTime),
                    # if 1 then make it a draft
                    sqla.Column("draft", sqla.SmallInteger, default=0),
                    info=self._info

                )
                self._logger.debug("Created table with table name %s" %
                                   post_table_name)
            else:
                self._post_table = self._metadata.tables[post_table_name]
                self._logger.debug("Reflecting to table with table name %s" %
                                   post_table_name)

    def _create_tag_table(self):
        """
        Creates the table to store blog post tags.
        :return:
        """
        with self._engine.begin() as conn:
            tag_table_name = self._table_name("tag")
            if not conn.dialect.has_table(conn, tag_table_name):
                self._tag_table = sqla.Table(
                    tag_table_name, self._metadata,
                    sqla.Column("id", sqla.Integer, primary_key=True),
                    sqla.Column("text", sqla.String(128), unique=True,
                                index=True),
                    info=self._info
                )
                self._logger.debug("Created table with table name %s" %
                                   tag_table_name)
            else:
                self._tag_table = self._metadata.tables[tag_table_name]
                self._logger.debug("Reflecting to table with table name %s" %
                                   tag_table_name)

    def _create_tag_posts_table(self):
        """
        Creates the table to store association info between blog posts and
        tags.
        :return:
        """
        with self._engine.begin() as conn:
            tag_posts_table_name = self._table_name("tag_posts")
            if not conn.dialect.has_table(conn, tag_posts_table_name):
                tag_id_key = self._table_name("tag") + ".id"
                post_id_key = self._table_name("post") + ".id"
                self._tag_posts_table = sqla.Table(
                    tag_posts_table_name, self._metadata,
                    sqla.Column('tag_id', sqla.Integer,
                                sqla.ForeignKey(tag_id_key, onupdate="CASCADE",
                                                ondelete="CASCADE"),
                                index=True),
                    sqla.Column('post_id', sqla.Integer,
                                sqla.ForeignKey(post_id_key,
                                                onupdate="CASCADE",
                                                ondelete="CASCADE"),
                                index=True),
                    sqla.UniqueConstraint('tag_id', 'post_id', name='uix_1'),
                    info=self._info
                )
                self._logger.debug("Created table with table name %s" %
                                   tag_posts_table_name)
            else:
                self._tag_posts_table = \
                    self._metadata.tables[tag_posts_table_name]
                self._logger.debug("Reflecting to table with table name %s" %
                                   tag_posts_table_name)

    def _create_user_posts_table(self):
        """
        Creates the table to store association info between user and blog
        posts.
        :return:
        """
        with self._engine.begin() as conn:
            user_posts_table_name = self._table_name("user_posts")
            if not conn.dialect.has_table(conn, user_posts_table_name):
                post_id_key = self._table_name("post") + ".id"
                self._user_posts_table = sqla.Table(
                    user_posts_table_name, self._metadata,
                    sqla.Column("user_id", sqla.String(128), index=True),
                    sqla.Column("post_id", sqla.Integer,
                                sqla.ForeignKey(post_id_key,
                                                onupdate="CASCADE",
                                                ondelete="CASCADE"),
                                index=True),
                    sqla.UniqueConstraint('user_id', 'post_id', name='uix_2'),
                    info=self._info
                )
                self._logger.debug("Created table with table name %s" %
                                   user_posts_table_name)
            else:
                self._user_posts_table = \
                    self._metadata.tables[user_posts_table_name]
                self._logger.debug("Reflecting to table with table name %s" %
                                   user_posts_table_name)
