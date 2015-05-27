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




class Storage(object):

    def save_post(self, title, text, user_id, tags, draft=False, post_id=None):
        raise NotImplementedError("This method needs to be implemented by the inheriting class")

    def get_post_by_id(self, post_id):
        raise NotImplementedError("This method needs to be implemented by the inheriting class")

    @staticmethod
    def normalize_tags(tags):
        return [tag.upper() for tag in tags]