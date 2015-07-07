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
to provide blog support to your existing web application. This is contrary
to some other packages such as `Flask-Blog <https://github.com/dmaslov/flask-blog>`_
that are just blogs. If you already have a
web app and you need to have a blog to communicate with your user or to
promote your site through content based marketing, then Flask-Blogging would help
you quickly get a blog up and running.

Out of the box, Flask-Blogging has support for the following:

- Bootstrap based site
- Markdown based blog editor
- Models to store blog
- Authentication of User's choice
- Sitemap, ATOM support
- Disqus support for comments
- Google analytics for usage tracking
- Well documented, tested, and extensible design

.. contents::
   :local:
   :backlinks: none

Quick Start Example
===================

.. code:: python

    from flask import Flask, render_template_string, redirect
    from sqlalchemy import create_engine
    from flask.ext.login import UserMixin, LoginManager, \
        login_user, logout_user
    from flask.ext.blogging import SQLAStorage, BloggingEngine

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret"  # for WTF-forms and login
    app.config["BLOGGING_URL_PREFIX"] = "/blog"
    app.config["BLOGGING_DISQUS_SITENAME"] = "test"
    app.config["BLOGGING_SITEURL"] = "http://localhost:8000"

    # extensions
    engine = create_engine('sqlite:////tmp/blog.db')
    sql_storage = SQLAStorage(engine)
    blog_engine = BloggingEngine(app, sql_storage)
    login_manager = LoginManager(app)

    # user class for providing authentication
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
            {% if current_user.is_authenticated() %}
                <a href="/logout/">Logout</a>
            {% else %}
                <a href="/login/">Login</a>
            {% endif %}
            &nbsp&nbsp<a href="/blog/">Blog</a>
            &nbsp&nbsp<a href="/blog/sitemap.xml">Sitemap</a>
            &nbsp&nbsp<a href="/blog/feeds/all.atom.xml">ATOM</a>
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


The key components required to get the blog hooked is explained below.

Configuring your Application
============================

The `BloggingEngine` class is the gateway to configure blogging support
to your web app. You should create the `BloggingEngine` instance like this::

    blogging_engine = BloggingEngine()

You also need to pick the storage for blog. That can be done as::

    from sqlalchemy import create_engine

    engine = create_engine("sqlite:////tmp/sqlite.db")
    storage = SQLAStorage(engine)

Once you have created the blogging engine and the storage, you can connect
with your app using the `init_app` method as shown below::

   blogging_engine.init_app(app, storage)

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

The ``BloggingEngine`` also accepts ``post_processor`` argument, which can be
used to provide a custom post processor object to handle the processing
of Markdown text. An ideal way to do this would be to inherit the default
``PostProcessor`` object and override custom methods. There is a
``custom_process`` method that can be overridden to add extra functionality
to the post processing step.

The ``BloggingEngine`` can be configured by setting the following app
config variables. These arguments are passed to all the views. The
keys that are currently supported include:

=========================== ===================================================
BLOGGING_SITENAME           The name of the blog to be used as the brand name
                            (default "Flask-Blogging")
BLOGGING_SITEURL            The url of the site.
BLOGGING_RENDER_TEXT        Boolean value to specify if the raw text should be
                            rendered or not. (default ``True``)
BLOGGING_DISQUS_SITENAME    Disqus sitename for comments (default ``None``)
BLOGGING_GOOGLE_ANALYTICS   Google analytics code for usage tracking
                            (default ``None``)
BLOGGING_URL_PREFIX         The prefix for the URL of blog posts
                            (default ``None``)
=========================== ===================================================



Blog Views
==========

There are various views that are exposed through Flask-Blogging. If the ``url_prefix``
argument in the BloggingEngine is ``/blog``, then the URL for the various views are:

- ``/blog/`` (GET): The index blog posts with the first page of articles.
- ``/blog/page/<post_id>/<optional slug>/`` (GET): The blog post corresponding to the ``post_id`` is retrieved.
- ``/blog/tag/<tag_name>/`` (GET): The list of blog posts corresponding to ``tag_name`` is returned.
- ``/blog/author/<user_id>/`` (GET): The list of blog posts written by the author ``user_id`` is returned.
- ``/blog/editor/`` (GET, POST): The blog editor is shown. This view needs authentication.
- ``/blog/delete/<post_id>/`` (POST): The blog post given by ``post_id`` is deleted. This view needs authentication.
- ``/blog/sitemap.xml`` (GET): The sitemap with a link to all the posts is returned.

The view can be easily customised by the user by overriding with their own templates. The template pages that need
to be customized are:

- ``blog/index.html``: The blog index page used to serve index of posts, posts by tag, and posts by author
- ``blog/editor.html``: The blog editor page.
- ``blog/page.html``: The page that shows the given article.
- ``blog/sitemap.xml``: The sitemap for the blog posts.

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
- If you use ``psycopg2`` driver for Postgres while using the ``SQLAStorage``
  you would need to have ``autocommit`` turned on while creating the engine::

    create_engine("postgresql+psycopg2://postgres:@localhost/flask_blogging",
                  isolation_level="AUTOCOMMIT")


Compatibility Notes
===================
- In version 0.2.0

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


.. include:: releases.rst

.. include:: authors.rst
