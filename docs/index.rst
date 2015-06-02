.. Flask-Blogging documentation master file, created by
   sphinx-quickstart on Fri May 29 12:51:58 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==============
Flask-Blogging
==============

Flask-Blogging is a Flask extension for adding blog support to your site.
It provides a flexible mechanism to store the data in the database
of your choice. It is meant to work with the authentication
provided by packages such as `Flask-Login <https://flask-login.readthedocs.org/en/latest/>`_
or `Flask-Security <https://pythonhosted.org/Flask-Security/>`_.

The philosophy behind this extension is to provide a lean app based on markdown
to provide blog support to your existing web application. This is contrary
to some other packages such as that are just blogs. If you already have a
web app and you need to have a blog to communicate with your user or to
promote your site through content based marketing.

.. contents::
   :local:
   :backlinks: none

Configuring your Application
============================

The `BloggingEngine` class is the gateway to configure blogging support
to your web app. You should create the `BloggingEngine` instance like this::

    blogging_engine = BloggingEngine()

You also need to pick the storage for blog. That can be done as::

    from sqlalchemy import create_engine

    engine = create_engine("sqlite:////tmp/sqlite.db")
    storage = SQLAStorage(engine)

Once you have created the blogging engine and the storage, you can connect with your app using
the `init_app` method as shown below::

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

.. automodule:: flask_blogging.processor
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



