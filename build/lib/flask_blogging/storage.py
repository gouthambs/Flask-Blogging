try:
    from builtins import object
except ImportError:
    pass


class Storage(object):

    def save_post(self, title, text, user_id, tags, draft=False,
                  post_date=None, last_modified_date=None, meta_data=None,
                  post_id=None):
        """
        Persist the blog post data. If ``post_id`` is ``None`` or ``post_id``
        is invalid, the post must be inserted into the storage. If ``post_id``
        is a valid id, then the data must be updated.

        :param title: The title of the blog post
        :type title: str
        :param text: The text of the blog post
        :type text: str
        :param user_id: The user identifier
        :type user_id: str
        :param tags: A list of tags
        :type tags: list
        :param draft: If the post is a draft of if needs to be published.
        :type draft: bool
        :param post_date: (Optional) The date the blog was posted (default
         datetime.datetime.utcnow())
        :type post_date: datetime.datetime
        :param last_modified_date: (Optional) The date when blog was last
         modified  (default datetime.datetime.utcnow())
        :type last_modified_date: datetime.datetime
        :param meta_data: The meta data for the blog post
        :type meta_data: dict
        :param post_id: The post identifier. This should be ``None`` for an
         insert call, and a valid value for update.
        :type post_id: int

        :return: The post_id value, in case of a successful insert or update.
        Return ``None`` if there were errors.
        """
        raise NotImplementedError("This method needs to be implemented by "
                                  "the inheriting class")

    def get_post_by_id(self, post_id):
        """
        Fetch the blog post given by ``post_id``

        :param post_id: The post identifier for the blog post
        :type post_id: int
        :return: If the ``post_id`` is valid, the post data is retrieved,
        else returns ``None``.
        """
        raise NotImplementedError("This method needs to be implemented by the "
                                  "inheriting class")

    def get_posts(self, count=10, offset=0, recent=True,  tag=None,
                  user_id=None, include_draft=False):
        """
        Get posts given by filter criteria

        :param count: The number of posts to retrieve (default 10). If count
         is ``None``, all posts are returned.
        :type count: int
        :param offset: The number of posts to offset (default 0)
        :type offset: int
        :param recent: Order by recent posts or not
        :type recent: bool
        :param tag: Filter by a specific tag
        :type tag: str
        :param user_id: Filter by a specific user
        :type user_id: str
        :param include_draft: Whether to include posts marked as draft or not
        :type include_draft: bool

        :return: A list of posts, with each element a dict containing values
         for the following keys: (title, text, draft, post_date,
         last_modified_date). If count is ``None``, then all the posts are
         returned.
        """
        raise NotImplementedError("This method needs to be implemented by the "
                                  "inheriting class")

    def count_posts(self, tag=None, user_id=None, include_draft=False):
        """
        Returns the total number of posts for the give filter

        :param tag: Filter by a specific tag
        :type tag: str
        :param user_id: Filter by a specific user
        :type user_id: str
        :param include_draft: Whether to include posts marked as draft or not
        :type include_draft: bool
        :return: The number of posts for the given filter.
        """
        raise NotImplementedError("This method needs to be implemented by the "
                                  "inheriting class")

    def delete_post(self, post_id):
        """
        Delete the post defined by ``post_id``

        :param post_id: The identifier corresponding to a post
        :type post_id: int
        :return: Returns True if the post was successfully deleted and False
         otherwise.
        """
        raise NotImplementedError("This method needs to be implemented by the "
                                  "inheriting class")

    @staticmethod
    def normalize_tags(tags):
        return [tag.upper().strip() for tag in tags]
