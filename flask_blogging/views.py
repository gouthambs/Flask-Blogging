from flask.ext.login import login_required, current_user
from flask import Blueprint, current_app, render_template
from flask_blogging.forms import BlogEditor


blog_app = Blueprint("blog_app", __name__, template_folder='templates')


def _get_blogging_engine(app):
    return app.extensions["FLASK_BLOGGING_ENGINE"]


def _get_user_name(user):
    user_name = user.get_name() if hasattr(user, "get_name") else str(user)
    return user_name


def _process_post(post, blogging_engine, author=None):
    post_processors = blogging_engine.post_processors
    for post_processor in post_processors:
        post_processor.process(post)
    if author is None:
        if blogging_engine.user_callback is None:
            raise Exception("No user_loader has been installed for this BloggingEngine."
                            " Add one with the 'BloggingEngine.user_loader' decorator.")
        author = blogging_engine.user_callback(post["user_id"])
    if author is not None:
        post["user_name"] = _get_user_name(author)



@blog_app.route("/", defaults={"count": 10, "offset": 0})
@blog_app.route("/<int:count>/", defaults={"offset": 0})
@blog_app.route("/<int:count>/<int:offset>/")
def index(count, offset):
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    posts = storage.get_posts(count=count, offset=offset)
    for post in posts:
        _process_post(post, blogging_engine)
    return render_template("blog/index.html", posts=posts, config=blogging_engine.config)


@blog_app.route("/page/<int:post_id>/", defaults={"slug": ""})
@blog_app.route("/page/<int:post_id>/<slug>/")
def page_by_id(post_id, slug):
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    post = storage.get_post_by_id(post_id)
    _process_post(post, blogging_engine)
    return render_template("blog/page.html", post=post, config=blogging_engine.config)


@blog_app.route("/tag/<tag>/", defaults=dict(count=10, offset=0))
@blog_app.route("/tag/<tag>/<int:count>/<int:offset>/")
def posts_by_tag(tag, count, offset):
    blogging_engine = current_app.extensions["FLASK_BLOGGING_ENGINE"]
    storage = blogging_engine.storage
    posts = storage.get_posts(count=count, offset=offset, tag=tag)
    for post in posts:
        _process_post(post, blogging_engine)
    return render_template("blog/index.html", posts=posts, config=blogging_engine.config)



@blog_app.route('/editor')
#@login_required
def editor():
    blogging_engine = current_app.extensions["FLASK_BLOGGING_ENGINE"]
    form = BlogEditor()
    return render_template("blog/editor.html", form=form, config=blogging_engine.config)

