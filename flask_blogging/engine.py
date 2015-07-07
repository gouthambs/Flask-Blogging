"""
The BloggingEngine module.
"""
try:
    from builtins import object
except ImportError:
    pass
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
    def __init__(self, app=None, storage=None, post_processor=None,
                 extensions=None):
        """

        :param app: Optional app to use
        :type app: object
        :param storage: The blog storage instance that implements the
         ``Storage`` class interface.
        :type storage: object
        :param post_processor: (optional) The post processor object. If none
         provided, the default post processor is used.
        :type post_processor: object
        :param extensions: A list of markdown extensions to add to post
         processing step.
        :type extensions: list
        :return:
        """
        self.app = None
        self.storage = None
        self.post_processor = PostProcessor() if post_processor is None \
            else post_processor
        if extensions:
            self.post_processor.set_custom_extensions(extensions)
        self.user_callback = None

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
        self.config = self.app.config
        self.storage = storage
        from flask_blogging.views import blog_app
        self.app.register_blueprint(
            blog_app, url_prefix=self.config.get("BLOGGING_URL_PREFIX"))
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
