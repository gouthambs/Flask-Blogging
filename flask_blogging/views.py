
from flask import Blueprint, current_app, render_template, url_for
from flask_blogging.utils import create_slug

blog_app = Blueprint("blog_app", __name__, template_folder='templates')

@blog_app.route("/", defaults={"count": 10, "offset": 0})
@blog_app.route("/<int:count>", defaults={"offset": 0})
@blog_app.route("/<int:count>/<int:offset>")
def index(count, offset):
    blogging_engine = current_app.extensions["FLASK_BLOGGING_ENGINE"]
    post_processor = blogging_engine.post_processor
    storage = blogging_engine.storage
    posts = storage.get_posts(count=count, offset=offset)
    for post in posts:
        post_processor.process(post)
    return render_template("blog/index.html", posts=posts)


@blog_app.route("/page/<int:post_id>/", defaults={"slug": ""})
@blog_app.route("/page/<int:post_id>/<slug>")
def page_by_id(post_id, slug):
    blogging_engine = current_app.extensions["FLASK_BLOGGING_ENGINE"]
    post_processor = blogging_engine.post_processor
    storage = blogging_engine.storage
    post = storage.get_post_by_id(post_id)
    post_processor.process(post)
    return render_template("blog/page.html", post=post)


@blog_app.route("/tag/<tag>", defaults=dict(count=10, offset=0))
@blog_app.route("/tag/<tag>/<int:count>/<int:offset>")
def posts_by_tag(tag, count, offset):
    blogging_engine = current_app.extensions["FLASK_BLOGGING_ENGINE"]
    post_processor = blogging_engine.post_processor
    storage = blogging_engine.storage
    posts = storage.get_posts(count=count, offset=offset, tag=tag)
    for post in posts:
        post_processor.process(post)
    return render_template("blog/index.html", posts=posts)


