from flask_blogging import signals, BloggingEngine
from flask import Blueprint
from werkzeug.contrib.atom import AtomFeed


# receivers for various signals
def blueprint_created_receiver(sender, engine, blueprint):
    assert sender == engine.app
    isinstance(engine, BloggingEngine)
    isinstance(blueprint, Blueprint)
    engine.ctr_blueprint_created += 1


def sitemap_posts_receiver(sender, engine, posts):
    assert sender == engine.app
    isinstance(engine, BloggingEngine)
    isinstance(posts, list)
    engine.ctr_sitemap_posts += 1


def feed_posts_fetched_receiver(sender, engine, posts):
    assert sender == engine.app
    isinstance(engine, BloggingEngine)
    isinstance(posts, list)
    engine.ctr_feed_posts_fetched += 1


def feed_posts_processed_receiver(sender, engine, feed):
    assert sender == engine.app
    isinstance(engine, BloggingEngine)
    isinstance(feed, AtomFeed)
    engine.ctr_feed_posts_processed += 1


def index_posts_receiver(sender, engine, posts, meta):
    assert sender == engine.app
    isinstance(engine, BloggingEngine)
    isinstance(posts, list)
    isinstance(meta, dict)
    isinstance(meta["count"], int)
    isinstance(meta["page"], int)
    engine.ctr_index_posts += 1


def page_by_id_receiver(sender, engine, post, meta):
    assert sender == engine.app
    isinstance(engine, BloggingEngine)
    isinstance(post, dict)
    isinstance(meta, dict)
    isinstance(meta["post_id"], int)
    isinstance(meta["slug"], str)
    engine.ctr_page_by_id += 1


def posts_by_tag_receiver(sender, engine, posts, meta):
    assert sender == engine.app
    isinstance(engine, BloggingEngine)
    isinstance(posts, list)
    isinstance(meta, dict)
    isinstance(meta["tag"], str)
    isinstance(meta["count"], int)
    isinstance(meta["page"], int)
    engine.ctr_posts_by_tag += 1


def posts_by_author_receiver(sender, engine, posts, meta):
    assert sender == engine.app
    isinstance(engine, BloggingEngine)
    isinstance(posts, list)
    isinstance(meta, dict)
    isinstance(meta["user_id"], str)
    isinstance(meta["count"], int)
    isinstance(meta["page"], int)
    engine.ctr_posts_by_author += 1


def register(app):
    signals.blueprint_created.connect(blueprint_created_receiver)

    signals.sitemap_posts_fetched.connect(sitemap_posts_receiver)
    signals.sitemap_posts_processed.connect(sitemap_posts_receiver)

    signals.feed_posts_fetched.connect(feed_posts_fetched_receiver)
    signals.feed_posts_processed.connect(feed_posts_processed_receiver)

    signals.index_posts_fetched.connect(index_posts_receiver)
    signals.index_posts_processed.connect(index_posts_receiver)

    signals.page_by_id_fetched.connect(page_by_id_receiver)
    signals.page_by_id_processed.connect(page_by_id_receiver)

    signals.posts_by_tag_fetched.connect(posts_by_tag_receiver)
    signals.posts_by_tag_processed.connect(posts_by_tag_receiver)

    signals.posts_by_author_fetched.connect(posts_by_author_receiver)
    signals.posts_by_author_processed.connect(posts_by_author_receiver)


def disconnect_receivers(app):
    signals.blueprint_created.disconnect(blueprint_created_receiver)

    signals.sitemap_posts_fetched.disconnect(sitemap_posts_receiver)
    signals.sitemap_posts_processed.disconnect(sitemap_posts_receiver)

    signals.feed_posts_fetched.disconnect(feed_posts_fetched_receiver)
    signals.feed_posts_processed.disconnect(feed_posts_processed_receiver)

    signals.index_posts_fetched.disconnect(index_posts_receiver)
    signals.index_posts_processed.disconnect(index_posts_receiver)

    signals.page_by_id_fetched.disconnect(page_by_id_receiver)
    signals.page_by_id_processed.disconnect(page_by_id_receiver)

    signals.posts_by_tag_fetched.disconnect(posts_by_tag_receiver)
    signals.posts_by_tag_processed.disconnect(posts_by_tag_receiver)

    signals.posts_by_author_fetched.disconnect(posts_by_author_receiver)
    signals.posts_by_author_processed.disconnect(posts_by_author_receiver)
