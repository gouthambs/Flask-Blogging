Release Notes
=============

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

- **Version 0.2.0**:

    In this version, ``BloggingEngine`` will no longer take ``config``
    argument. Instead, all configuration can be done through ``app`` config
    variables. Another ``BloggingEngine`` parameter, ``url_prefix`` is also
    available only through config variable.
