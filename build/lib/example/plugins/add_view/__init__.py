
from flask_blogging import signals
from flask_blogging.views import sitemap


def add_custom_view(app, engine, blueprint):
    """
    Make sitemap page available from /sitemap as well
    """
    blueprint.add_url_rule("/sitemap", view_func=sitemap)


def register(app):
    signals.blueprint_created.connect(add_custom_view)



