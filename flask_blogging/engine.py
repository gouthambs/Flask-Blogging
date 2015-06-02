"""
The BloggingEngine module.
"""
from .processor import PostProcessor


class BloggingEngine(object):
    """
    The BloggingEngine is core class to add blogging support to
    your web app.
    """
    def __init__(self, app=None, storage=None, url_prefix=None, post_processors=None, config=None):
        """
        Creates the instance

        :param app: Optional app to use
        :param storage: The storage pertaining to the storage of choice.
        :return:
        """
        self.app = None
        self.storage = None
        self.url_prefix = url_prefix
        self.post_processors = [PostProcessor()] if post_processors is None else post_processors
        self.user_callback = None
        self.config = {} if config is None else config
        if app is not None and storage is not None:
            self.init_app(app, storage)

    def init_app(self, app, storage):
        self.app = app
        self.storage = storage
        from flask_blogging.views import blog_app
        self.app.register_blueprint(blog_app, url_prefix=self.url_prefix)
        self.app.extensions["FLASK_BLOGGING_ENGINE"] = self

    def user_loader(self, callback):
        self.user_callback = callback
        return callback
