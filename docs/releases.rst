Release Notes
=============

- **Version 2.0.0** (*Release February, 2022*)

 - Updates to be compatible with Flask 2.0
 - Improved unit testing and build / release pipeline

- **Version 1.2.2** (*Release January 31, 2019*)

 - Add file_upload optional argument to engine's init_app method (#133)

- **Version 1.2.1** (*Release January 20, 2019*)

 - Fix broken docs and update Flask-Fileupload configurations

- **Version 1.2.0** (*Release January 9, 2019*)

 - ``GoogleCloudDatastore`` provides Google clould support
 - Updated markdown js script

- **Version 1.1.0** (*Release September 12, 2018*)

 - SQLAStorage query optimization
 - Updated Disqus to latest
 - Some minor docs fixes

- **Version 1.0.2** (*Release September 2, 2017*)

 - Add social links
 - Add a choice to escape markdown input
 - Remove negative offset for ``SQLAStorage`` storage engine.

- **Version 1.0.1** (*Release July 22, 2017*)

 - Expanded the example with S3Storage for Flask-FileUpload
 - Post id for DynamoDB only uses lower case alphabet and numbers

- **Version 1.0.0** (*Release July 15, 2017*)

  - Added DynamoDB storage
  - Add Open Graph support

- **Version 0.9.2** (*Release June 25, 2017*)

  - Additional fixes to ``automap_base`` in creating ``Post`` and ``Tag`` models

- **Version 0.9.1** (*Release June 23, 2017*)

  - Fixes to ``automap_base`` in creating ``Post`` and ``Tag`` models
  - Some improvements to blog page generation


- **Version 0.9.0** (*Release Jun 17, 2017*)

  - Added information contained in the ``meta`` variable passed to the views as requested in (#102)
  - Add missing space to Prev pagination link text (#103)
  - Only render the modal of the user is a blogger (#101)
  - Added ``Post`` and ``Tag`` models in ``sqlastorage`` using ``automap_base``.


- **Version 0.8.0** (*Release May 16, 2017*)

  - Added integration with Flask-FileUpload to enable static file uploads (#99)
  - Updated compatibility to latest Flask-WTF package (#96, #97)
  - Updated to latest bootstrap-markdown package (#92)
  - Added alert fade outs (#94)


- **Version 0.7.4** (*Release November 17, 2016*)

  - Fix Requirements.txt error


- **Version 0.7.3** (*Release November 6, 2016*)
  
  - Fix issues with slugs with special characters (#80)


- **Version 0.7.2** (*Release October 30, 2016*)
  
  - Moved default static assets to https (#78)
  - Fixed the issue where post fetched wouldn't emit when no posts exist (#76)


- **Version 0.7.1** (*Released July 5, 2016*)
 
  - Improvements to docs
  - Added extension import transition (@slippers)


- **Version 0.7.0** (*Released May 25, 2016*)


- **Version 0.6.0** (*Released January 14, 2016*)

  - The plugin framework for Flask-Blogging to allow users to add new
    features and capabilities.


- **Version 0.5.2** (*Released January 12, 2016*)

  - Added support for multiple binds for SQLAStorage


- **Version 0.5.1** (*Released December 6, 2015*)

  - Fixed the flexibility to add custom extensions to `BloggingEngine`.


- **Version 0.5.0** (*Released November 23, 2015*)

  - Fixed errors encountered while using Postgres database


- **Version 0.4.2** (*Released September 20, 2015*)

  - Added compatibility with Flask-Login version 0.3.0 and higher, especially to handle migration of
    ``is_autheticated`` attribute from method to property. (#43)


- **Version 0.4.1** (*Released September 16, 2015*)

  - Added javascript to center images in blog page
  - Added method in blogging engine to render post and fetch post.


- **Version 0.4.0** (*Released July 26, 2015*)

  - Integrated Flask-Cache to optimize blog page rendering
  - Fixed a bug where anonymous user was shown the new blog button


- **Version 0.3.2** (*Released July 20, 2015*)

  - Fixed a bug in the edit post routines. The edited post would end up as a
    new one instead.


- **Version 0.3.1** (*Released July 17, 2015*)

  - The ``SQLAStorage`` accepts metadata, and ``SQLAlchemy`` object as inputs.
    This adds the ability to keep the blogging table metadata synced up with
    other models. This feature adds compatibility with ``Alembic`` autogenerate.
  - Update docs to reflect the correct version number.


- **Version 0.3.0** (*Released July 11, 2015*)

  - Permissions is a new feature introduced in this version. By setting
    ``BLOGGING_PERMISSIONS`` to ``True``, one can restrict which of the users
    can create, edit or delete posts.
  - Added ``BLOGGING_POSTS_PER_PAGE`` configuration variable to control
    the number of posts in a page.
  - Documented the url construction procedure.


- **Version 0.2.1** (*Released July 10, 2015*)

  - ``BloggingEngine`` ``init_app`` method can be called without having to
    pass a ``storage`` object.
  - Hook tests to ``setup.py`` script.


- **Version 0.2.0** (*Released July 6, 2015*)
    
    - ``BloggingEngine`` configuration moved to the ``app`` config setting.
      This breaks backward compatibility. See compatibility notes below.
    - Added ability to limit number of posts shown in the feed through
      ``app`` configuration setting.
    - The ``setup.py`` reads version from the module file. Improves version
      consistency.


- **Version 0.1.2** (*Released July 4, 2015*)
    
    - Added Python 3.4 support


- **Version 0.1.1** (*Released June 15, 2015*)
    
    - Fixed PEP8 errors
    - Expanded SQLAStorage to include Postgres and MySQL flavors
    - Added ``post_date`` and ``last_modified_date`` as arguments to the
      ``Storage.save_post(...)`` call for general compatibility


- **Version 0.1.0** (*Released June 1, 2015*)
    
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
