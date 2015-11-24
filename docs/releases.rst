Release Notes
=============

- **Version 0.5.0**

  *Released November 23, 2015*

  - Fixed errors encountered while using Postgres database

- **Version 0.4.2**

  *Released September 20, 2015*

  - Added compatibility with Flask-Login version 0.3.0 and higher, especially to handle migration of
    ``is_autheticated`` attribute from method to property. (#43)

- **Version 0.4.1**

  *Released September 16, 2015*

  - Added javascript to center images in blog page
  - Added method in blogging engine to render post and fetch post.


- **Version 0.4.0**

  *Released July 26, 2015*

  - Integrated Flask-Cache to optimize blog page rendering
  - Fixed a bug where anonymous user was shown the new blog button

- **Version 0.3.2**:

  *Released July 20, 2015*

  - Fixed a bug in the edit post routines. The edited post would end up as a
    new one instead.

- **Version 0.3.1**:

  *Released July 17, 2015*

  - The ``SQLAStorage`` accepts metadata, and ``SQLAlchemy`` object as inputs.
    This adds the ability to keep the blogging table metadata synced up with
    other models. This feature adds compatibility with ``Alembic`` autogenerate.
  - Update docs to reflect the correct version number.

- **Version 0.3.0**:

  *Released July 11, 2015*

  - Permissions is a new feature introduced in this version. By setting
    ``BLOGGING_PERMISSIONS`` to ``True``, one can restrict which of the users
    can create, edit or delete posts.
  - Added ``BLOGGING_POSTS_PER_PAGE`` configuration variable to control
    the number of posts in a page.
  - Documented the url construction procedure.

- **Version 0.2.1**:

  *Released July 10, 2015*

  - ``BloggingEngine`` ``init_app`` method can be called without having to
    pass a ``storage`` object.
  - Hook tests to ``setup.py`` script.

- **Version 0.2.0**:

  *Released July 6, 2015*
    
    - ``BloggingEngine`` configuration moved to the ``app`` config setting.
      This breaks backward compatibility. See compatibility notes below.
    - Added ability to limit number of posts shown in the feed through
      ``app`` configuration setting.
    - The ``setup.py`` reads version from the module file. Improves version
      consistency.

- **Version 0.1.2**:

  *Released July 4, 2015*
    
    - Added Python 3.4 support

- **Version 0.1.1**:

  *Released June 15, 2015*
    
    - Fixed PEP8 errors
    - Expanded SQLAStorage to include Postgres and MySQL flavors
    - Added ``post_date`` and ``last_modified_date`` as arguments to the
    ``Storage.save_post(...)`` call for general compatibility


- **Version 0.1.0**:

  *Released June 1, 2015*
    
    - Initial Release
    - Adds detailed documentation
    - Supports Markdown based blog editor
    - Has 90% code coverage in unit tests

Compatibility Notes
===================
- **Version 0.4.1**:

  The documented way to get the blogging engine from ``app`` is using
  the key ``blogging`` from ``app.extensions``.

- **Version 0.3.1**:

    The ``SQLAStorage`` will accept metadata and set it internally. The database
    tables will not be created automatically. The user would need to invoke
    ``create_all`` in the metadata or ``SQLAlchemy`` object in ``Flask-SQLAlchemy``.

- **Version 0.3.0**:

    - In this release, the templates folder was renamed from ``blog`` to
      ``blogging``. To override the existing templates, you will need to
      create your templates in the ``blogging`` folder.

    - The blueprint name was renamed from ``blog_api`` to ``blogging``.

- **Version 0.2.0**:

    In this version, ``BloggingEngine`` will no longer take ``config``
    argument. Instead, all configuration can be done through ``app`` config
    variables. Another ``BloggingEngine`` parameter, ``url_prefix`` is also
    available only through config variable.
