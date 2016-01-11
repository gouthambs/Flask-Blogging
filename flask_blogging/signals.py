"""
    The flask_blogging signals module

    :copyright: (c) 2012 by Matt Wright.
    :license: MIT, see LICENSE for more details.
"""


import blinker

signals = blinker.Namespace()

engine_initialised = signals.signal("engine_initialised", doc="""\
Signal send by the ``BloggingEngine`` after the object is initialized.
The arguments passed by the signal are:

:param app: The Flask app which is the sender
:type app: object
:keyword engine: The blogging engine that was initialized
:type engine: object
""")

post_processed = signals.signal("post_processed", doc="""\
Signal sent when a post is processed (i.e., the markdown is converted
to html text). The arguments passed along with this signal are:

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param post: The post object which was processed
:type post: dict
:param render: Flag to denote if the post is to be rendered or not
:type render: bool
""")

page_by_id_fetched = signals.signal("page_by_id_fetched", doc="""\
Signal sent when a blog page specified by ``id`` is fetched,
and prior to the post being processed.

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param post: The post object which was fetched
:type post: dict
:param meta: The metadata associated with that page
:type meta: dict
:param post_id: The identifier of the post
:type post_id: int
:param slug: The slug associated with the page
:type slug: str
""")
page_by_id_processed = signals.signal("page_by_id_generated", doc="""\
Signal sent when a blog page specified by ``id`` is fetched,
and prior to the post being processed.

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param post: The post object which was processed
:type post: dict
:param meta: The metadata associated with that page
:type meta: dict
:param post_id: The identifier of the post
:type post_id: int
:param slug: The slug associated with the page
:type slug: str
""")

posts_by_tag_fetched = signals.signal("posts_by_tag_fetched", doc="""\
Signal sent when posts are fetched for a given tag but before processing

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param posts: Lists of post fetched with a given tag
:type post: list
:param meta: The metadata associated with that page
:type meta: dict
:param tag: The tag that is requested
:type tag: str
:param count: The number of posts per page
:type count: int
:param page: The page offset
:type page: int
""")

posts_by_tag_processed = signals.signal("posts_by_tag_generated", doc="""\
Signal sent after posts for a given tag were fetched and processed

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param posts: Lists of post fetched and processed with a given tag
:type post: list
:param meta: The metadata associated with that page
:type meta: dict
:param tag: The tag that is requested
:type tag: str
:param count: The number of posts per page
:type count: int
:param page: The page offset
:type page: int
""")

posts_by_author_fetched = signals.signal("posts_by_author_fetched", doc="""\
Signal sent after posts by an author were fetched but before processing

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param posts: Lists of post fetched and processed with a given author
:type post: list
:param meta: The metadata associated with that page
:type meta: dict
:param user_id: The ``user_id`` for the author
:type user_id: str
:param count: The number of posts per page
:type count: int
:param page: The page offset
:type page: int
""")
posts_by_author_processed = signals.signal("posts_by_author_generated",
                                           doc="""\
Signal sent after posts by an author were fetched and processed

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param posts: Lists of post fetched and processed with a given author
:type post: list
:param meta: The metadata associated with that page
:type meta: dict
:param user_id: The ``user_id`` for the author
:type user_id: str
:param count: The number of posts per page
:type count: int
:param page: The page offset
:type page: int
""")

index_posts_fetched = signals.signal("index_posts_fetched")
index_posts_processed = signals.signal("index_posts_processed")

feed_posts_fetched = signals.signal("feed_posts_fetched")
feed_posts_processed = signals.signal("feed_posts_processed")

sitemap_posts_fetched = signals.signal("sitemap_posts_fetched")
sitemap_posts_processed = signals.signal("sitemap_posts_processed")

editor_post_saved = signals.signal("editor_post_saved")
editor_get_fetched = signals.signal("editor_get_fetched")

post_deleted = signals.signal("post_deleted")

blueprint_created = signals.signal("blueprint_created")

sqla_initialized = signals.signal("sqla_initialized")

