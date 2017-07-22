import os
import logging
from threading import Lock
from .storage import Storage
import pandas as pd
import json


class FileStorage(Storage):
    _logger = logging.getLogger("flask-blogging")
    _mutex_index = Lock() # lock while operating on the index files
    _mutex_post = Lock()  # lock while operating on the post files

    def __init__(self, blog_dir):
        self._blog_dir = blog_dir
        self._setup_blog_dir()

    def save_post(self, title, text, user_id, tags, draft=False,
                  post_date=None, last_modified_date=None, meta_data=None,
                  post_id=None):
        post = self._read_post(post_id) if post_id else {}
        post["title"] = title
        post["text"] = text
        post["user_id"] = user_id
        post["tags"] = tags
        post["draft"] = draft
        post["post_date"] = post_date
        post["last_modified_date"] = last_modified_date
        post["meta_data"] = meta_data




    def get_post_by_id(self, post_id):
        pass


    def _read_post(self, post_id):
        post_file = os.path.join(self._posts_dir, "%d.json" % post_id)
        if os.path.exists(post_file):
            fp = open(post_file, "r")
            post = json.load(fp)
        else:
            post = None
        return post

    def _setup_blog_dir(self):
        self._posts_dir = os.path.join(self._blog_dir, "posts")
        if not os.path.exists(self._posts_dir):
            os.mkdir(self._posts_dir)
        self._trash_dir = os.path.join(self._blog_dir, "trash")
        if not os.path.exists(self._trash_dir):
            os.mkdir(self._trash_dir)
        self._post_index = os.path.join(self._blog_dir, "post_index")
        if not os.path.exists(self._post_index):
            columns = ["post_id", "title", "post_date", "last_modified_date", "draft", "deleted"]
            self._df_post = pd.DataFrame(columns=columns).set_index("post_id")
            self._df_post.to_msgpack(self._post_index)
        else:
            self._df_post = pd.read_msgpack(self._post_index)
        self._author_index = os.path.join(self._blog_dir, "author_index")
        if not os.path.exists(self._author_index):
            columns = ["user_id", "post_id"]
            self._df_author = pd.DataFrame(columns=columns).set_index("user_id")
            self._df_author.to_msgpack(self._author_index)
        else:
            self._df_author = pd.read_msgpack(self._author_index)
        self._tag_index = os.path.join(self._blog_dir, "tag_index")
        if not os.path.exists(self._tag_index):
            columns = ["tag", "post_id"]
            self._df_tag = pd.DataFrame(columns=columns).set_index("tag")
            self._df_tag.to_msgpack(self._tag_index)
        else:
            self._df_tag = pd.read_msgpack(self._tag_index)