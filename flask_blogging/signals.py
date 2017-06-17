"""
    The flask_blogging signals module

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
""")

posts_by_tag_fetched = signals.signal("posts_by_tag_fetched", doc="""\
Signal sent when posts are fetched for a given tag but before processing

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param posts: Lists of post fetched with a given tag
:type posts: list
:param meta: The metadata associated with that page
:type meta: dict
""")

posts_by_tag_processed = signals.signal("posts_by_tag_generated", doc="""\
Signal sent after posts for a given tag were fetched and processed

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param posts: Lists of post fetched and processed with a given tag
:type posts: list
:param meta: The metadata associated with that page
:type meta: dict
""")

posts_by_author_fetched = signals.signal("posts_by_author_fetched", doc="""\
Signal sent after posts by an author were fetched but before processing

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param posts: Lists of post fetched with a given author
:type posts: list
:param meta: The metadata associated with that page
:type meta: dict
""")
posts_by_author_processed = signals.signal("posts_by_author_generated",
                                           doc="""\
Signal sent after posts by an author were fetched and processed

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param posts: Lists of post fetched and processed with a given author
:type posts: list
:param meta: The metadata associated with that page
:type meta: dict
""")

index_posts_fetched = signals.signal("index_posts_fetched", doc="""\
Signal sent after the posts for the index page are fetched

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param posts: Lists of post fetched for the index page
:type posts: list
:param meta: The metadata associated with that page
:type meta: dict
""")

index_posts_processed = signals.signal("index_posts_processed", doc="""\
Signal sent after the posts for the index page are fetched and processed

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param posts: Lists of post fetched and processed with a given author
:type posts: list
:param meta: The metadata associated with that page
:type meta: dict
""")

feed_posts_fetched = signals.signal("feed_posts_fetched", doc="""\
Signal send after feed posts are fetched

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param posts: Lists of post fetched and processed with a given author
:type posts: list
""")
feed_posts_processed = signals.signal("feed_posts_processed", doc="""\
Signal send after feed posts are processed

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param feed: Feed of post fetched and processed
:type feed: list
""")

sitemap_posts_fetched = signals.signal("sitemap_posts_fetched", doc="""\
Signal send after posts are fetched

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param posts: Lists of post fetched and processed with a given author
:type posts: list
""")
sitemap_posts_processed = signals.signal("sitemap_posts_processed", doc="""\
Signal send after posts are fetched and processed

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param posts: Lists of post fetched and processed with a given author
:type posts: list
""")

editor_post_saved = signals.signal("editor_post_saved", doc="""\
Signal sent after a post was saved during the POST request

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param post_id: The id of the post that was deleted
:type post_id: int
:param user: The user object
:type user: object
:param post: The post that was deleted
:type post: object

""")
editor_get_fetched = signals.signal("editor_get_fetched", doc="""\
Signal sent after fetching the post during the GET request

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param post_id: The id of the post that was deleted
:type post_id: int
:param form: The form prepared for the editor display
:type form: object
""")

post_deleted = signals.signal("post_deleted", doc="""\
The signal sent after the post is deleted.

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param post_id: The id of the post that was deleted
:type post_id: int
:param post: The post that was deleted
:type post: object
""")

blueprint_created = signals.signal("blueprint_created", doc="""\
The signal sent after the blueprint is created. A good time to
add other views to the blueprint.

:param app: The Flask app which is the sender
:type app: object
:param engine: The blogging engine that was initialized
:type engine: object
:param blueprint: The blog app blueprint
:type blueprint: object

""")

sqla_initialized = signals.signal("sqla_initialized", doc="""\
Signal sent after the SQLAStorage object is initialized

:param sqlastorage: The SQLAStorage object
:type sqlastorage: object
:param engine: The blogging engine that was initialized
:type engine: object
:param table_prefix: The prefix to use for tables
:type table_prefix: str
:param meta: The metadata for the database
:type meta: object
:param bind: The bind value in the multiple db scenario.
:type bind: object
""")
