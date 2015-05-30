class Storage(object):

    def save_post(self, title, text, user_id, tags, draft=False, post_id=None):
        """
        Persist the blog post data. If post_id is None or post_id is invalid, the post must
        be inserted into the storage. If post_id is a valid id, then the data must be updated.
        :param title:
        :type title: str
        :param text:
        :param user_id:
        :param tags:
        :param draft:
        :param post_id:
        :return: The post_id value, in case of insert or update
        """
        raise NotImplementedError("This method needs to be implemented by the inheriting class")

    def get_post_by_id(self, post_id):
        """
        Fetch the blog post given by post_id
        :param post_id: the identifier for the blog post
        :type post_id: int
        :return:
        """
        raise NotImplementedError("This method needs to be implemented by the inheriting class")

    def get_posts(self, count=10, offset=0, recent=True,  tag=None, user_id=None):
        """
        Get posts given by filter criteria
        :param count:
        :param offset:
        :param recent:
        :param tag:
        :param user_id:
        :return:
        """
        raise NotImplementedError("This method needs to be implemented by the inheriting class")

    def delete_post(self, post_id):
        """

        :param post_id:
        :return:
        """
        raise NotImplementedError("This method needs to be implemented by the inheriting class")

    @staticmethod
    def normalize_tags(tags):
        return [tag.upper().strip() for tag in tags]

