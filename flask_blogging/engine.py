"""
The BloggingEngine module.
"""
try:
    from builtins import object
except ImportError:
    pass
from .processor import PostProcessor
from flask.ext.principal import Principal, Permission, RoleNeed


class BloggingEngine(object):
    """
    The BloggingEngine is the class for initializing the blog support for your
    web app. Here is an example usage:

    .. code:: python

        from flask import Flask
        from flask.ext.blogging import BloggingEngine, SQLAStorage
        from sqlalchemy import create_engine

        app = Flask(__name__)
        db_engine = create_engine("sqlite:////tmp/sqlite.db")
        meta = MetaData()
        storage = SQLAStorage(db_engine, metadata=meta)
        blog_engine = BloggingEngine(app, storage)
    """
    def __init__(self, app=None, storage=None, post_processor=None,
                 extensions=None, cache=None):
        """

        :param app: Optional app to use
        :type app: object
        :param storage: The blog storage instance that implements the
         ``Storage`` class interface.
        :type storage: object
        :param post_processor: (optional) The post processor object. If none
         provided, the default post processor is used.
        :type post_processor: object
        :param extensions: (optional) A list of markdown extensions to add to
         post processing step.
        :type extensions: list
        :param cache: (Optional) A Flask-Cache object to enable caching
        :type cache: Object
        :return:
        """
        self.app = None
        self.storage = storage
        self.cache = cache
        self._blogger_permission = None
        self.post_processor = PostProcessor() if post_processor is None \
            else post_processor
        if extensions:
            self.post_processor.set_custom_extensions(extensions)
        self.user_callback = None

        if app is not None and storage is not None:
            self.init_app(app, storage)

    def init_app(self, app, storage=None, cache=None):
        """
        Initialize the engine.

        :param app: The app to use
        :type app: Object
        :param storage: The blog storage instance that implements the
        :type storage: Object
        :param cache: (Optional) A Flask-Cache object to enable caching
        :type cache: Object
         ``Storage`` class interface.
        """
        self.app = app
        self.config = self.app.config
        self.storage = storage or self.storage
        self.cache = cache or self.cache

        from .views import create_blueprint
        self.app.register_blueprint(
            create_blueprint(__name__, self),
            url_prefix=self.config.get("BLOGGING_URL_PREFIX"))
        self.app.extensions["FLASK_BLOGGING_ENGINE"] = self
        self.principal = Principal(self.app)

    @property
    def blogger_permission(self):
        if self._blogger_permission is None:
            if self.config.get("BLOGGING_PERMISSIONS", False):
                self._blogger_permission = Permission(RoleNeed("blogger"))
            else:
                self._blogger_permission = Permission()
        return self._blogger_permission

    def user_loader(self, callback):
        """
        The decorator for loading the user.

        :param callback: The callback function that can load a user given a
         unicode ``user_id``.
        :return: The callback function
        """
        self.user_callback = callback
        return callback

    def is_user_blogger(self):
        return self.blogger_permission.require().can()
