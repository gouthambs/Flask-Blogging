Flask-Blogging
==============

.. image:: https://travis-ci.org/gouthambs/Flask-Blogging.svg?branch=master
    :target: https://travis-ci.org/gouthambs/Flask-Blogging


This is a Flask extension for adding blog support to your site using Markdown.
Please see
`Flask-Blogging documentation <http://flask-blogging.readthedocs.org/en/latest/>`_
for more details.

Screen Shots
------------

Blog Editor
~~~~~~~~~~~

.. figure:: /docs/_static/blog_editor.png

    Blog Editor

Blog Page
~~~~~~~~~

.. figure:: /docs/_static/blog_page.png

    Blog Page

Minimal Example
---------------

.. code:: python

    from flask import Flask, render_template_string, redirect
    from sqlalchemy import create_engine
    from flask.ext.login import UserMixin, LoginManager, login_user, logout_user
    from flask.ext.blogging import SQLAStorage, BloggingEngine
    
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret"  # for WTF-forms and login
    
    # extensions
    engine = create_engine('sqlite:////tmp/blog.db')
    sql_storage = SQLAStorage(engine)
    blog_engine = BloggingEngine(app, sql_storage, url_prefix="/blog",
                                 config={"DISQUS_SITENAME": "test",
                                         "SITEURL": "http://localhost:8000"})
    login_manager = LoginManager(app)
    
    
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
                <a href="/logout/"> Logout </a>
            {% else %}
                <a href="/login/"> Login </a>
            {% endif %}
            &nbsp&nbsp<a href="/blog/"> Blog </a>
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


Installation
------------

Install the extension with the following commands::

    $ easy_install flask-blogging
    
or alternatively if you have pip installed::

    $ pip install flask-blogging
    

Dependencies
------------

- `Flask <https://github.com/mitsuhiko/flask>`_
- `SQLAlchemy <https://github.com/zzzeek/sqlalchemy>`_
- `Flask-Login <https://github.com/maxcountryman/flask-login>`_
- `Flask-WTF <https://github.com/lepture/flask-wtf>`_
- `Markdown <https://pythonhosted.org/Markdown/>`_
- `Bootstrap <http://getbootstrap.com/>`_
- `Bootstrap-Markdown <https://github.com/toopay/bootstrap-markdown>`_
- `Markdown-js <https://github.com/evilstreak/markdown-js>`_

License
-------

`MIT </LICENSE>`_

.. include:: docs/releases.rst

.. include:: docs/authors.rst
