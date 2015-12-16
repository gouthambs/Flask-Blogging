"""
    The flask_blogging signals module

    :copyright: (c) 2012 by Matt Wright.
    :license: MIT, see LICENSE for more details.
"""


import blinker

signals = blinker.Namespace()

engine_initialised = signals.signal("engine_initialised")

post_processed = signals.signal("post_processed")

page_by_id_generated = signals.signal("page_by_id_generated")
posts_by_tag_generated = signals.signal("posts_by_tag_generated")
posts_by_author_generated = signals.signal("posts_by_author_generated")
index_generated = signals.signal("index_generated")




