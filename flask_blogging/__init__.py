__author__ = 'Gouthaman Balaraman'


class BloggingEngine(object):
    def __init__(self, app=None, storage=None):
        """
        Creates the instance

        :param app: Optional app to use
        :param storage: The storage pertaining to the storage of choice.
        :return:
        """
        self.app = None
        self.storage = None
        if app is not None and storage is not None:
            self.init_app(app, storage)

    def init_app(self, app, storage):
        self.app = app
        self.storage = storage



