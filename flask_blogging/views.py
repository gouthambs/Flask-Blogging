from flask.ext.login import login_required, current_user
from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash
from flask_blogging.forms import BlogEditor


blog_app = Blueprint("blog_app", __name__, template_folder='templates')


def _get_blogging_engine(app):
    return app.extensions["FLASK_BLOGGING_ENGINE"]


def _get_user_name(user):
    user_name = user.get_name() if hasattr(user, "get_name") else str(user)
    return user_name


def _process_post(post, blogging_engine, author=None, render=True):
    post_processor = blogging_engine.post_processor
    post_processor.process(post, render)
    if author is None:
        if blogging_engine.user_callback is None:
            raise Exception("No user_loader has been installed for this BloggingEngine."
                            " Add one with the 'BloggingEngine.user_loader' decorator.")
        author = blogging_engine.user_callback(post["user_id"])
    if author is not None:
        post["user_name"] = _get_user_name(author)


def _store_form_data(blog_form, storage, user, post_id):
    title = blog_form.title.data
    text = blog_form.text.data
    tags = blog_form.tags.data.split(",")
    draft = blog_form.draft.data
    user_id = user.get_id()
    pid = storage.save_post(title, text, user_id, tags, draft, post_id)
    return pid


@blog_app.route("/", defaults={"count": 10, "page": 1})
@blog_app.route("/<int:count>/", defaults={"page": 1})
@blog_app.route("/<int:count>/<int:page>/")
def index(count, page):
    """
    Serves the page with a list of blog posts

    :param count:
    :param offset:
    :return:
    """
    offset = max(0, (page-1)*count)
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    config = blogging_engine.config
    render = config.get("RENDER_TEXT", True)
    posts = storage.get_posts(count=count, offset=offset)
    for post in posts:
        _process_post(post, blogging_engine)
    return render_template("blog/index.html", posts=posts, config=config)


@blog_app.route("/page/<int:post_id>/", defaults={"slug": ""})
@blog_app.route("/page/<int:post_id>/<slug>/")
def page_by_id(post_id, slug):
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    post = storage.get_post_by_id(post_id)
    if post is not None:
        _process_post(post, blogging_engine)
        return render_template("blog/page.html", post=post, config=blogging_engine.config)
    else:
        flash("The page you are trying to access is not valid!", "warning")
        return redirect(url_for("blog_app.index"))



@blog_app.route("/tag/<tag>/", defaults=dict(count=10, page=1))
@blog_app.route("/tag/<tag>/<int:count>/", defaults=dict(page=1))
@blog_app.route("/tag/<tag>/<int:count>/<int:page>/")
def posts_by_tag(tag, count, page):
    meta = {}
    offset = max(0, (page-1)*count)
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    posts = storage.get_posts(count=count, offset=offset, tag=tag)
    for post in posts:
        _process_post(post, blogging_engine)
    return render_template("blog/index.html", posts=posts, config=blogging_engine.config)


@blog_app.route("/author/<user_id>/", defaults=dict(count=10, page=1))
@blog_app.route("/author/<user_id>/<int:count>/", defaults=dict(page=1))
@blog_app.route("/author/<user_id>/<int:count>/<int:page>/")
def posts_by_author(user_id, count, page):
    offset = max(0, (page-1)*count)
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    posts = storage.get_posts(count=count, offset=offset, user_id=user_id)
    if len(posts):
        for post in posts:
            _process_post(post, blogging_engine)
    else:
        flash("No posts found for this user!", "warning")
    return render_template("blog/index.html", posts=posts, config=blogging_engine.config)


@blog_app.route('/editor/', methods=["GET", "POST"], defaults={"post_id": None})
@blog_app.route('/editor/<int:post_id>/', methods=["GET", "POST"])
@login_required
def editor(post_id):
    blogging_engine = _get_blogging_engine(current_app)
    post_processor = blogging_engine.post_processor
    storage = blogging_engine.storage
    if request.method == 'POST':
        form = BlogEditor(request.form)
        if form.validate():
            pid = _store_form_data(form, storage, current_user, post_id)
            flash("Blog post posted successfully!", "info")
            slug = post_processor.create_slug(form.title.data)
            return redirect(url_for("blog_app.page_by_id", post_id=pid, slug=slug))
        else:
            flash("There were errors in the blog submission", "warning")
            return render_template("blog/editor.html", form=form, post_id=post_id, config=blogging_engine.config)
    else:
        if post_id is not None:
            post = storage.get_post_by_id(post_id)
            if (post is not None) and (current_user.get_id() == post["user_id"]):
                tags = ", ".join(post["tags"])
                form = BlogEditor(title=post["title"], text=post["text"], tags=tags )
                return render_template("blog/editor.html", form=form, post_id=post_id, config=blogging_engine.config)
            else:
                flash("You do not have the rights to edit this post", "warning")
                return redirect(url_for("blog_app.editor", post_id=None))
                
    form = BlogEditor()
    return render_template("blog/editor.html", form=form, post_id=post_id, config=blogging_engine.config)


@blog_app.route("/delete/<int:post_id>/", methods=["POST"])
@login_required
def delete(post_id):
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    post = storage.get_post_by_id(post_id)
    if (post is not None) and (current_user.get_id() == post["user_id"]):
        success = storage.delete_post(post_id)
        if success:
            flash("Your post was successfully deleted", "info")
        else:
            flash("Something went wrong while deleting your post", "warning")
    else:
        flash("You do not have the rights to delete this post", "warning")
    return redirect(url_for("blog_app.index"))
