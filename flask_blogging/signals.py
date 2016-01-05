"""
    The flask_blogging signals module

    :copyright: (c) 2012 by Matt Wright.
    :license: MIT, see LICENSE for more details.
"""


import blinker

signals = blinker.Namespace()

engine_initialised = signals.signal("engine_initialised")

post_processed = signals.signal("post_processed")

page_by_id_fetched = signals.signal("page_by_id_fetched")
page_by_id_processed = signals.signal("page_by_id_generated")

posts_by_tag_fetched = signals.signal("posts_by_tag_fetched")
posts_by_tag_processed = signals.signal("posts_by_tag_generated")

posts_by_author_fetched = signals.signal("posts_by_author_fetched")
posts_by_author_processed = signals.signal("posts_by_author_generated")

index_posts_fetched = signals.signal("index_posts_fetched")
index_posts_processed = signals.signal("index_posts_processed")

feed_posts_fetched = signals.signal("feed_posts_fetched")
feed_posts_processed = signals.signal("feed_posts_processed")

sitemap_posts_fetched = signals.signal("sitemap_posts_fetched")
sitemap_posts_processed = signals.signal("sitemap_posts_processed")

blueprint_created = signals.signal("blueprint_created")


sqla_initialized = signals.signal("sqla_initialized")
sqla_post_saved = signals.signal("sqla_post_saved")
