.. Flask-Blogging documentation master file, created by
   sphinx-quickstart on Fri May 29 12:51:58 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==============
Flask-Blogging
==============

Flask-Blogging is a Flask extension for adding Markdown based blog support to your site.
It provides a flexible mechanism to store the data in the database
of your choice. It is meant to work with the authentication
provided by packages such as
`Flask-Login <https://flask-login.readthedocs.org/en/latest/>`_ or
`Flask-Security <https://pythonhosted.org/Flask-Security/>`_.

The philosophy behind this extension is to provide a lean app based on Markdown
to provide blog support to your existing web application. If you already have a
web app and you need to have a blog to communicate with your user or to
promote your site through content based marketing, then Flask-Blogging would help
you quickly get a blog up and running.

Out of the box, Flask-Blogging has support for the following:

- Bootstrap based site
- Markdown based blog editor
- Upload and manage static assets for the blog
- Models to store blog
- Authentication of User's choice
- Sitemap, ATOM support
- Disqus support for comments
- Google analytics for usage tracking
- Open Graph meta tags
- Permissions enabled to control which users can create/edit blogs
- Integrated Flask-Cache based caching for optimization
- Well documented, tested, and extensible design
- DynamoDB storage for use in AWS
- Google Cloud Datastore support

.. contents::
   :local:
   :backlinks: none

Quick Start Example
===================

.. code:: python

    from flask import Flask, render_template_string, redirect
    from sqlalchemy import create_engine, MetaData
    from flask_login import UserMixin, LoginManager, login_user, logout_user
    from flask_blogging import SQLAStorage, BloggingEngine

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret"  # for WTF-forms and login
    app.config["BLOGGING_URL_PREFIX"] = "/blog"
    app.config["BLOGGING_DISQUS_SITENAME"] = "test"
    app.config["BLOGGING_SITEURL"] = "http://localhost:8000"
    app.config["BLOGGING_SITENAME"] = "My Site"
    app.config["BLOGGING_KEYWORDS"] = ["blog", "meta", "keywords"]
    app.config["FILEUPLOAD_LOCALSTORAGE_IMG_FOLDER"] = "img_upload"
    app.config["FILEUPLOAD_PREFIX"] = "/fileupload"
    app.config["FILEUPLOAD_ALLOWED_EXTENSIONS"] = ["png", "jpg", "jpeg", "gif"]

    # extensions
    engine = create_engine('sqlite:////tmp/blog.db')
    meta = MetaData()
    sql_storage = SQLAStorage(engine, metadata=meta)
    blog_engine = BloggingEngine(app, sql_storage)
    login_manager = LoginManager(app)
    meta.create_all(bind=engine)


    class User(UserMixin):
        def __init__(self, user_id):
            self.id = user_id

        def get_name(self):
            return "Paul Dirac"  # typically the user's name

    @login_manager.user_loader
    @blog_engine.user_loader
    def load_user(user_id):
        return User(user_id)

    index_template = """
    <!DOCTYPE html>
    <html>
        <head> </head>
        <body>
            {% if current_user.is_authenticated %}
                <a href="/logout/"> Logout </a>
            {% else %}
                <a href="/login/"> Login </a>
            {% endif %}
            &nbsp&nbsp<a href="/blog/"> Blog </a>
            &nbsp&nbsp<a href="/blog/sitemap.xml">Sitemap</a>
            &nbsp&nbsp<a href="/blog/feeds/all.atom.xml">ATOM</a>
            &nbsp&nbsp<a href="/fileupload/">FileUpload</a>
        </body>
    </html>
    """

    @app.route("/")
    def index():
        return render_template_string(index_template)

    @app.route("/login/")
    def login():
        user = User("testuser")
        login_user(user)
        return redirect("/blog")

    @app.route("/logout/")
    def logout():
        logout_user()
        return redirect("/")


    if __name__ == "__main__":
        app.run(debug=True, port=8000, use_reloader=True)


The key components required to get the blog hooked is explained below. Please note
that as of Flask-Login 0.3.0 the ``is_authenticated`` attribute in the ``UserMixin``
is a property and not a method. Please use the appropriate option based on your
Flask-Login version. You can find more examples here in the
`Flask-Blogging github project page <https://github.com/gouthambs/Flask-Blogging/tree/master/example>`_.

Configuring your Application
============================

The ``BloggingEngine`` class is the gateway to configure blogging support
to your web app. You should create the ``BloggingEngine`` instance like this::

    blogging_engine = BloggingEngine()
    blogging_engine.init_app(app, storage)

You also need to pick the ``storage`` for blog. That can be done as::

    from sqlalchemy import create_engine, MetaData

    engine = create_engine("sqlite:////tmp/sqlite.db")
    meta = MetaData()
    storage = SQLAStorage(engine, metadata=meta)
    meta.create_all(bind=engine)

Here we have created the storage, and created all the tables
in the metadata. Once you have created the blogging engine,
storage, and all the tables in the storage, you can connect
with your app using the ``init_app`` method as shown below::

   blogging_engine.init_app(app, storage)

If you are using ``Flask-Sqlalchemy``, you can do the following::

    from flask_sqlalchemy import SQLAlchemy

    db = SQLAlchemy(app)
    storage = SQLAStorage(db=db)
    db.create_all()

One of the changes in version 0.3.1 is the ability for the user
to provide the ``metadata`` object. This has the benefit of the
table creation being passed to the user. Also, this gives the user
the ability to use the common metadata object, and hence helps
with the tables showing up in migrations while using Alembic.

As of version 0.5.2, support for the multi database scenario
under Flask-SQLAlchemy was added. When we have a multiple database
scenario, one can use the ``bind`` keyword in ``SQLAStorage`` to
specify the database to bind to, as shown below::

    # config value
    SQLALCHEMY_BINDS = {
        'blog': "sqlite:////tmp/blog.db"),
        'security': "sqlite:////tmp/security.db")
    }

The storage can be initialised as::

    db = SQLAlchemy(app)
    storage = SQLAStorage(db=db, bind="blog")
    db.create_all()

As of version 0.4.0, Flask-Cache integration is supported. In order
to use caching in the blogging engine, you need to pass the ``Cache``
instance to the ``BloggingEngine`` as::

    from flask_caching import Cache
    from flask_blogging import BloggingEngine

    blogging_engine = BloggingEngine(app, storage, cache)


*Flask-Blogging* lets the developer pick the authentication
that is suitable, and hence requires her to provide a way to load user
information. You will need to provide a `BloggingEngine.user_loader`
callback. This callback is used to load the user from the `user_id`
that is stored for each blog post. Just as in Flask-Login, it should take the
`unicode` `user_id` of a user, and return the corresponding user
object. For example::

    @blogging_engine.user_loader
    def load_user(userid):
        return User.get(userid)


For the blog to have a readable display name, the ``User`` class must
implement either the ``get_name`` method or the ``__str__`` method.

The ``BloggingEngine`` accepts an optional ``extensions`` argument. This is a list
of ``Markdown`` extensions objects to be used during the markdown processing step.

As of version 0.6.0, a plugin interface is available to add new functionality.
Custom processes can be added to the ``posts`` by subscribing to the
``post_process_before`` and ``post_process_after`` signals, and adding
new functionality to it.

The ``BloggingEngine`` also accepts ``post_processor`` argument, which can be
used to provide a custom post processor object to handle the processing
of Markdown text. One way to do this would be to inherit the default
``PostProcessor`` object and override ``process`` method.

In version 0.4.1 and onwards, the ``BloggingEngine`` object can be accessed
from your ``app`` as follows::

    engine = app.extensions["blogging"]

The engine method also exposes a ``get_posts`` method to get the recent posts
for display of posts in other views.

In earlier versions the same can be done using the key
``FLASK_BLOGGING_ENGINE`` instead of ``blogging``. The use of
``FLASK_BLOGGING_ENGINE`` key will be deprecated moving forward.


Models from SQLAStorage
-----------------------

`SQLAlchemy` ORM models for the `SQLAStorage` can be accessed after
configuration of the `SQLAStorage` object. Here is a quick example::

    storage = SQLAStorage(db=db)
    from flask_blogging.sqlastorage import Post, Tag  # Has to be after SQLAStorage initialization

These ORM models can be extremely convenient to use with Flask-Admin.



Adding Custom Markdown Extensions
---------------------------------

One can provide additional MarkDown extensions to the blogging engine.
One example usage is adding the ``codehilite`` MarkDown extension. Additional
extensions should be passed as a list while initializing the ``BlogggingEngine``
as shown::

    from markdown.extensions.codehilite import CodeHiliteExtension

    extn1 = CodeHiliteExtension({})
    blogging_engine = BloggingEngine(app, storage,extensions=[extn1])


This allows for the MarkDown to be processed using CodeHilite along with
the default extensions. Please note that one would also need to include
necessary static files in the ``view``, such as for code highlighting to work.

Extending using Markdown Metadata
---------------------------------

Let's say you want to include a summary for your blog post, and have it
show up along with the post. You don't need to modify the database or
the models to accomplish this. This is in fact supported by default by way
of Markdown metadata syntax. In your blog post, you can include metadata,
as shown below::

    Summary: This is a short summary of the blog post
    Keywords: Blog, specific, keywords

    This is the much larger blog post. There are lot of things
    to discuss here.

In the template ``page.html`` this metadata can be accessed as, ``post.meta.summary``
and can be populated in the way it is desired. The same metadata for each post
is also available in other template views like ``index.html``.

If included, the first summary will be used as the page's meta ``description``,
and Open Graph ``og:description``.

The (optional) blog post specific keywords are included in the page's meta
keywords in addition to ``BLOGGING_KEYWORDS`` (if configured). Any tags are also
added as meta keywords.



Extending using the plugin framework
------------------------------------

The plugin framework is a very powerful way to modify the behavior of the
blogging engine. Lets say you want to show the top 10 most popular tag in the
post. Lets show how one can do that using the plugins framework. As a first step,
we create our plugin::

    # plugins/tag_cloud/__init__.py
    from flask_blogging import signals
    from flask_blogging.sqlastorage import SQLAStorage
    import sqlalchemy as sqla
    from sqlalchemy import func


    def get_tag_data(sqla_storage):
        engine = sqla_storage.engine
        with engine.begin() as conn:
            tag_posts_table = sqla_storage.tag_posts_table
            tag_table = sqla_storage.tag_table

            tag_cloud_stmt = sqla.select([
                tag_table.c.text,func.count(tag_posts_table.c.tag_id)]).group_by(
                tag_posts_table.c.tag_id
            ).where(tag_table.c.id == tag_posts_table.c.tag_id).limit(10)
            tag_cloud = conn.execute(tag_cloud_stmt).fetchall()
        return tag_cloud


    def get_tag_cloud(app, engine, posts, meta):
        if isinstance(engine.storage, SQLAStorage):
            tag_cloud = get_tag_data(engine.storage)
            meta["tag_cloud"] = tag_cloud
        else:
            raise RuntimeError("Plugin only supports SQLAStorage. Given storage"
                               "not supported")
        return


    def register(app):
        signals.index_posts_fetched.connect(get_tag_cloud)
        return


The ``register`` method is what is invoked in order to register the plugin. We have
connected this plugin to the ``index_posts_fetched`` signal. So when the posts are
fetched to show on the index page, this signal will be fired, and this plugin will
be invoked. The plugin basically queries the table that stores the tags, and returns
the tag text and the number of times it is referenced. The data about the tag cloud
we are storing in the ``meta["tag_cloud"]`` which corresponds to the metadata variable.


Now in the `index.html` template, one can reference the ``meta.tag_cloud`` to access this
data for display. The plugin can be registered by setting the config variable as shown::

    app.config["BLOGGING_PLUGINS"] = ["plugins.tag_cloud"]



Configuration Variables
=======================

The Flask-Blogging extension can be configured by setting the following app
config variables. These arguments are passed to all the views. The
keys that are currently supported include:

- ``BLOGGING_SITENAME`` (*str*): The name of the blog to be used as the brand
  name. This is also used in the feed heading and ``og:site_name`` meta tag.
  (default "Flask-Blogging")
- ``BLOGGING_SITEURL`` (*str*): The url of the site. This is also used in the
  ``og:publisher`` meta tag.
- ``BLOGGING_BRANDURL`` (*str*): The url of the site brand.
- ``BLOGGING_TWITTER_USERNAME`` (*str*): @name to tag social sharing link with.
- ``BLOGGING_RENDER_TEXT`` (*bool*): Value to specify if the raw text (markdown)
  should be rendered to HTML. (default ``True``)
- ``BLOGGING_DISQUS_SITENAME`` (*str*): Disqus sitename for comments.
  A ``None`` value will disable comments. (default ``None``)
- ``BLOGGING_GOOGLE_ANALYTICS`` (*str*): Google analytics code for usage
  tracking. A ``None`` value will disable google analytics. (default ``None``)
- ``BLOGGING_URL_PREFIX`` (*str*) : The prefix for the URL of blog posts. A
  ``None`` value will have no prefix. (default ``None``)
- ``BLOGGING_FEED_LIMIT`` (*int*): The number of posts to limit to in the feed.
  If ``None``, then all are shown, else will be limited to this number. (default ``None``)
- ``BLOGGING_PERMISSIONS`` (*bool*): If ``True``, this will enable permissions
  for the blogging engine. With permissions enabled, the user will need to have
  "blogger" ``Role`` to edit or create blog posts. Other authenticated
  users will not have blog editing permissions. The concepts here derive
  from ``Flask-Principal``. (default ``False``)
- ``BLOGGING_PERMISSIONNAME`` (*str*): The role name used for permissions.
  It is effective, if "BLOGGING_PERMISSIONS" is "True". (default "blogger")
- ``BLOGGING_POSTS_PER_PAGE`` (*int*): The default number of posts per index page.
  to be displayed per page. (default 10)
- ``BLOGGING_CACHE_TIMEOUT`` (*int*): The timeout in seconds used to cache.
  the blog pages. (default 60)
- ``BLOGGING_PLUGINS`` (*list*): A list of plugins to register.
- ``BLOGGING_KEYWORDS`` (*list*): A list of meta keywords to include on each page.
- ``BLOGGING_ALLOW_FILEUPLOAD`` (*bool*): Allow static file uploads ``flask_fileupload``
- ``BLOGGING_ESCAPE_MARKDOWN`` (*bool*): Escape input markdown text input. This is ``False`` by
  default. Set this to ``True`` to forbid embedding HTML in markdown.

Blog Views
==========

There are various views that are exposed through Flask-Blogging. The URL for
the various views are:

- ``url_for('blogging.index')`` (GET): The index blog posts with the first
  page of articles. The ``meta`` variable passed into the view holds values
  for the keys ``is_user_blogger``, ``count`` and ``page``.
- ``url_for('blogging.page_by_id', post_id=<post_id>)`` (GET): The blog post
  corresponding to the ``post_id`` is retrieved. The ``meta`` variable passed
  into the view holds values for the keys ``is_user_blogger``, ``post_id`` and
  ``slug``.
- ``url_for('blogging.posts_by_tag', tag=<tag_name>)`` (GET): The list of blog
  posts corresponding to ``tag_name`` is returned. The ``meta`` variable passed
  into the view holds values for the keys ``is_user_blogger``, ``tag``, ``count`` and
  ``page``.
- ``url_for('blogging.posts_by_author', user_id=<user_id>)`` (GET): The list of
  blog posts written by the author ``user_id`` is returned. The ``meta`` variable passed
  into the view holds values for the keys ``is_user_blogger``, ``count``, ``user_id`` and
  ``pages``.
- ``url_for('blogging.editor')`` (GET, POST): The blog editor
  is shown. This view needs authentication and permissions (if enabled).
- ``url_for('blogging.delete', post_id=<post_id>)`` (POST): The blog post
  given by ``post_id`` is deleted. This view needs authentication and
  permissions (if enabled).
- ``url_for('blogging.sitemap')`` (GET): The sitemap
  with a link to all the posts is returned.
- ``url_for('blogging.feed')`` (GET): Returns ATOM feed URL.

The view can be easily customised by the user by overriding with their own templates. The template pages that need
to be customized are:

- ``blogging/index.html``: The blog index page used to serve index of posts, posts by tag, and posts by author
- ``blogging/editor.html``: The blog editor page.
- ``blogging/page.html``: The page that shows the given article.
- ``blogging/sitemap.xml``: The sitemap for the blog posts.

Permissions
===========

In version 0.3.0 Flask-Blogging, enables permissions based on Flask-Principal.
This addresses the issue of controlling which of the authenticated users can
have access to edit or create blog posts. Permissions are enabled by setting
``BLOGGING_PERMISSIONS`` to ``True``. Only users that have access to
``Role`` "blogger" will have permissions to create or edit blog posts.


Screenshots
===========
Blog Page
---------
.. image:: _static/blog_page.png

Blog Editor
-----------
.. image:: _static/blog_editor.png

Useful Tips
===========

- **Migrations with Alembic**: (Applies to versions 0.3.0 and earlier)
  If you have migrations part of your project
  using Alembic, or extensions such as ``Flask-Migrate`` which uses Alembic, then
  you have to modify the ``Alembic`` configuration in order for it to ignore
  the ``Flask-Blogging`` related tables. If you don't set these modifications,
  then every time you run migrations, ``Alembic`` will not recognize the
  tables and mark them for deletion. And if you happen to ``upgrade`` by mistake
  then all your blog tables will be deleted. What we will do here is ask
  Alembic to ``exclude`` the tables used by ``Flask-Blogging``. In your
  ``alembic.ini`` file, add a line::

    [alembic:exclude]
    tables = tag, post, tag_posts, user_posts

  If you have a value set for ``table_prefix`` argument while creating the ``SQLAStorage``,
  then the table names will contain that prefix in their names. In which case, you have
  to use appropriate names in the table names.

  And in your ``env.py``, we have to mark these tables as the ones to be
  ignored.

  ::

    def exclude_tables_from_config(config_):
        tables_ = config_.get("tables", None)
        if tables_ is not None:
            tables = tables_.split(",")
        return tables

    exclude_tables = exclude_tables_from_config(config.get_section('alembic:exclude'))

    def include_object(object, name, type_, reflected, compare_to):
        if type_ == "table" and name in exclude_tables:
            return False
        else:
            return True

    def run_migrations_online():
        """Run migrations in 'online' mode.

        In this scenario we need to create an Engine
        and associate a connection with the context.

        """
        engine = engine_from_config(
                    config.get_section(config.config_ini_section),
                    prefix='sqlalchemy.',
                    poolclass=pool.NullPool)

        connection = engine.connect()
        context.configure(
                    connection=connection,
                    target_metadata=target_metadata,
                    include_object=include_object,
                    compare_type=True
                    )

        try:
            with context.begin_transaction():
                context.run_migrations()
        finally:
            connection.close()

  In the above, we are using ``include_object`` in ``context.configure(...)``
  to be specified based on the ``include_object`` function.



.. include:: releases.rst


API Documentation
=================

Module contents
---------------

.. automodule:: flask_blogging
    :members:
    :undoc-members:
    :show-inheritance:


Submodules
----------

flask_blogging.engine module
----------------------------

.. automodule:: flask_blogging.engine
    :members:
    :undoc-members:
    :show-inheritance:

flask_blogging.processor module
-------------------------------

.. autoclass:: flask_blogging.processor.PostProcessor
    :members:
    :undoc-members:
    :show-inheritance:

flask_blogging.sqlastorage module
---------------------------------

.. automodule:: flask_blogging.sqlastorage
    :members:
    :undoc-members:
    :show-inheritance:

flask_blogging.storage module
-----------------------------

.. automodule:: flask_blogging.storage
    :members:
    :undoc-members:
    :show-inheritance:

flask_blogging.views module
---------------------------

.. automodule:: flask_blogging.views
    :members:
    :undoc-members:
    :show-inheritance:

flask_blogging.forms module
---------------------------

.. automodule:: flask_blogging.forms
    :members:
    :undoc-members:

flask_blogging.signals module
---------------------------

.. automodule:: flask_blogging.signals
    :members: engine_initialised

.. autodata:: flask_blogging.signals

.. autodata:: flask_blogging.signals.engine_initialised

.. autodata:: flask_blogging.signals.post_processed

.. autodata:: flask_blogging.signals.page_by_id_fetched

.. autodata:: flask_blogging.signals.page_by_id_processed

.. autodata:: flask_blogging.signals.posts_by_tag_fetched

.. autodata:: flask_blogging.signals.posts_by_tag_processed

.. autodata:: flask_blogging.signals.posts_by_author_fetched

.. autodata:: flask_blogging.signals.posts_by_author_processed

.. autodata:: flask_blogging.signals.index_posts_fetched

.. autodata:: flask_blogging.signals.index_posts_processed

.. autodata:: flask_blogging.signals.feed_posts_fetched

.. autodata:: flask_blogging.signals.feed_posts_processed


.. autodata:: flask_blogging.signals.sitemap_posts_fetched

.. autodata:: flask_blogging.signals.sitemap_posts_processed

.. autodata:: flask_blogging.signals.editor_post_saved

.. autodata:: flask_blogging.signals.editor_get_fetched

.. autodata:: flask_blogging.signals.post_deleted

.. autodata:: flask_blogging.signals.blueprint_created

.. autodata:: flask_blogging.signals.sqla_initialized


.. include:: authors.rst
