"""
The BloggingEngine module.
"""
from .processor import PostProcessor


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
        storage = SQLAStorage(db_engine)
        blog_engine = BloggingEngine(app, storage)
    """
    def __init__(self, app=None, storage=None, url_prefix=None,
                 post_processor=None, config=None, extensions=None):
        """

        :param app: Optional app to use
        :type app: object
        :param storage: The blog storage instance that implements the
         ``Storage`` class interface.
        :type storage: object
        :param url_prefix: (optional) The prefix for the URL of blog posts
         (default ``None``)
        :type url_prefix: str
        :param post_processor: (optional) The post processor object. If none
         provided, the default post processor is used.
        :type post_processor: object
        :param config: (optional) A dictionary of config values. See docs for
         the keys that can be specified.
        :type config: dict
        :param extensions: A list of markdown extensions to add to post
         processing step.
        :type extensions: list
        :return:
        """
        self.app = None
        self.storage = None
        self.url_prefix = url_prefix
        self.post_processor = PostProcessor() if post_processor is None \
            else post_processor
        if extensions:
            self.post_processor.set_custom_extensions(extensions)
        self.user_callback = None

        self.config = {} if config is None else config
        if app is not None and storage is not None:
            self.init_app(app, storage)

    def init_app(self, app, storage):
        """
        Initialize the engine.

        :param app: The app to use
        :param storage: The blog storage instance that implements the
         ``Storage`` class interface.
        """
        self.app = app
        self.storage = storage
        from flask_blogging.views import blog_app
        self.app.register_blueprint(blog_app, url_prefix=self.url_prefix)
        self.app.extensions["FLASK_BLOGGING_ENGINE"] = self

    def user_loader(self, callback):
        """
        The decorator for loading the user.

        :param callback: The callback function that can load a user given a
         unicode ``user_id``.
        :return: The callback function
        """
        self.user_callback = callback
        return callback
