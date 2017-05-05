"""
The BloggingEngine module.
"""
try:
    from builtins import object
except ImportError:
    pass
from .processor import PostProcessor
from flask_principal import Principal, Permission, RoleNeed
from .signals import engine_initialised, post_processed, blueprint_created
from flask_fileupload import FlaskFileUpload


class BloggingEngine(object):
    """
    The BloggingEngine is the class for initializing the blog support for your
    web app. Here is an example usage:

    .. code:: python

        from flask import Flask
        from flask_blogging import BloggingEngine, SQLAStorage
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
        self.config = None
        self.ffu = None
        self.cache = cache
        self._blogger_permission = None
        self.post_processor = PostProcessor() if post_processor is None \
            else post_processor
        if extensions:
            self.post_processor.set_custom_extensions(extensions)
        self.user_callback = None

        if app is not None and storage is not None:
            self.init_app(app, storage)
        self.principal = None

    @classmethod
    def _register_plugins(cls, app, config):
        plugins = config.get("BLOGGING_PLUGINS")
        if plugins:
            for plugin in plugins:
                lib = __import__(plugin, globals(), locals(), str("module"))
                lib.register(app)

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
        self._register_plugins(self.app, self.config)

        from .views import create_blueprint
        blog_app = create_blueprint(__name__, self)
        # external urls
        blueprint_created.send(self.app, engine=self, blueprint=blog_app)
        self.app.register_blueprint(
            blog_app, url_prefix=self.config.get("BLOGGING_URL_PREFIX"))

        self.app.extensions["FLASK_BLOGGING_ENGINE"] = self  # duplicate
        self.app.extensions["blogging"] = self
        self.principal = Principal(self.app)
        engine_initialised.send(self.app, engine=self)

        self.ffu = FlaskFileUpload(app)

    @property
    def blogger_permission(self):
        if self._blogger_permission is None:
            if self.config.get("BLOGGING_PERMISSIONS", False):
                self._blogger_permission = Permission(RoleNeed(
                    self.config.get("BLOGGING_PERMISSIONNAME", "blogger")))
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

    def get_posts(self, count=10, offset=0, recent=True, tag=None,
                  user_id=None, include_draft=False, render=False):
        posts = self.storage(count, offset, recent, tag, user_id,
                             include_draft)
        for post in posts:
            self.process_post(post, render=False)

    def process_post(self, post, render=True):
        """
        A high level view to create post processing.
        :param post: Dictionary representing the post
        :type post: dict
        :param render: Choice if the markdown text has to be converted or not
        :type render: bool
        :return:
        """
        post_processor = self.post_processor
        post_processor.process(post, render)
        try:
            author = self.user_callback(post["user_id"])
        except Exception:
                raise Exception("No user_loader has been installed for this "
                                "BloggingEngine. Add one with the "
                                "'BloggingEngine.user_loader' decorator.")
        if author is not None:
            post["user_name"] = self.get_user_name(author)
        post_processed.send(self.app, engine=self, post=post, render=render)

    @classmethod
    def get_user_name(cls, user):
        user_name = user.get_name() if hasattr(user, "get_name") else str(user)
        return user_name
