Flask-Blogging
==============

.. image:: https://travis-ci.org/gouthambs/Flask-Blogging.svg?branch=master
    :target: https://travis-ci.org/gouthambs/Flask-Blogging


This is a Flask extension for adding blog support to your site using Markdown.
Please see `Flask-Blogging documentation <http://flask-blogging.readthedocs.org/en/latest/>`_
for more details. You can extend Flask-Blogging by using `plugins from here <https://github.com/gouthambs/blogging_plugins>`_.

Features
--------

- Integration with Markdown Editor
- Ability to upload images for use in blog pages
- Incorporate math formulas in LaTeX format
- Integrates with authentication to allow multiple users
- Plugin framework to easily extend and add new features


Sponsor
-------

`ButterCMS <https://buttercms.com/?utm_source=github&utm_medium=sponsorship-link&utm_campaign=flask-blogging>`_ is an API-based CMS and blogging platform built for developers:

.. image:: https://dl.dropboxusercontent.com/u/598519/buttercms-banners/b-on-y-m.png
    :target: https://buttercms.com/?utm_source=github&utm_medium=sponsorship-banner&utm_campaign=flask-blogging
    
Screen Shots
------------

    Blog Editor

.. figure:: /docs/_static/blog_editor.png

    Blog Page

.. figure:: /docs/_static/blog_page.png


Minimal Example
---------------

Check the `quickstart example <http://flask-blogging.readthedocs.org/en/latest/#quick-start-example>`_ for the latest documentation.

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
- `Flask-Principal <https://github.com/mattupstate/flask-principal>`_
- `Flask-WTF <https://github.com/lepture/flask-wtf>`_
- `Flask-FileUpload <https://github.com/Speedy1991/Flask-FileUpload>`_
- `Markdown <https://pythonhosted.org/Markdown/>`_
- `Bootstrap <http://getbootstrap.com/>`_
- `Bootstrap-Markdown <https://github.com/toopay/bootstrap-markdown>`_
- `Markdown-js <https://github.com/evilstreak/markdown-js>`_


License
-------

`MIT </LICENSE>`_

.. include:: /docs/releases.rst

.. include:: /docs/authors.rst
