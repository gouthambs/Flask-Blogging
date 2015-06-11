from flask.ext.login import login_required, current_user
from flask import Blueprint, current_app, render_template, request, redirect, \
    url_for, flash, make_response
from flask_blogging.forms import BlogEditor
import math
from werkzeug.contrib.atom import AtomFeed
import datetime


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
            raise Exception("No user_loader has been installed for this "
                            "BloggingEngine. Add one with the "
                            "'BloggingEngine.user_loader' decorator.")
        author = blogging_engine.user_callback(post["user_id"])
    if author is not None:
        post["user_name"] = _get_user_name(author)


def _store_form_data(blog_form, storage, user, post):
    title = blog_form.title.data
    text = blog_form.text.data
    tags = blog_form.tags.data.split(",")
    draft = blog_form.draft.data
    user_id = user.get_id()
    current_datetime = datetime.datetime.utcnow()
    post_date = post.get("post_date", current_datetime)
    last_modified_date = datetime.datetime.utcnow()
    post_id = post.get("post_id")
    pid = storage.save_post(title, text, user_id, tags, draft, post_date,
                            last_modified_date, post_id)
    return pid


def _get_meta(storage, count, page, tag=None, user_id=None):
    max_posts = storage.count_posts(tag=tag, user_id=user_id)
    max_pages = math.ceil(float(max_posts)/float(count))
    max_offset = (max_pages-1)*count
    offset = min(max(0, (page-1)*count), max_offset)
    if (tag is None) and (user_id is None):
        prev_page = None if page <= 1 else url_for(
            "blog_app.index", count=count, page=page-1)
        next_page = None if page >= max_pages else url_for(
            "blog_app.index", count=count, page=page+1)
    elif tag:
        prev_page = None if page <= 1 else url_for(
            "blog_app.posts_by_tag", tag=tag, count=count, page=page-1)
        next_page = None if page >= max_pages else url_for(
            "blog_app.posts_by_tag", tag=tag, count=count, page=page+1)
    elif user_id:
        prev_page = None if page <= 1 else url_for(
            "blog_app.posts_by_author", user_id=user_id, count=count,
            page=page-1)
        next_page = None if page >= max_pages else url_for(
            "blog_app.posts_by_author", user_id=user_id, count=count,
            page=page+1)
    else:
        prev_page = next_page = None

    pagination = dict(prev_page=prev_page, next_page=next_page)
    meta = dict(max_posts=max_posts, max_pages=max_pages, page=page,
                max_offset=max_offset, offset=offset, count=count,
                pagination=pagination)
    return meta


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
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    config = blogging_engine.config

    meta = _get_meta(storage, count, page)
    offset = meta["offset"]

    render = config.get("RENDER_TEXT", True)
    posts = storage.get_posts(count=count, offset=offset, include_draft=False,
                              tag=None, user_id=None, recent=True)
    for post in posts:
        _process_post(post, blogging_engine, render=render)
    return render_template("blog/index.html", posts=posts, meta=meta,
                           config=config)


@blog_app.route("/page/<int:post_id>/", defaults={"slug": ""})
@blog_app.route("/page/<int:post_id>/<slug>/")
def page_by_id(post_id, slug):
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    config = blogging_engine.config
    post = storage.get_post_by_id(post_id)

    render = config.get("RENDER_TEXT", True)
    if post is not None:
        _process_post(post, blogging_engine, render=render)
        return render_template("blog/page.html", post=post, config=config)
    else:
        flash("The page you are trying to access is not valid!", "warning")
        return redirect(url_for("blog_app.index"))


@blog_app.route("/tag/<tag>/", defaults=dict(count=10, page=1))
@blog_app.route("/tag/<tag>/<int:count>/", defaults=dict(page=1))
@blog_app.route("/tag/<tag>/<int:count>/<int:page>/")
def posts_by_tag(tag, count, page):
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    config = blogging_engine.config
    meta = _get_meta(storage, count, page, tag=tag)
    offset = meta["offset"]

    render = config.get("RENDER_TEXT", True)
    posts = storage.get_posts(count=count, offset=offset, tag=tag,
                              include_draft=False, user_id=None, recent=True)
    for post in posts:
        _process_post(post, blogging_engine, render=render)
    return render_template("blog/index.html", posts=posts, meta=meta,
                           config=config)


@blog_app.route("/author/<user_id>/", defaults=dict(count=10, page=1))
@blog_app.route("/author/<user_id>/<int:count>/", defaults=dict(page=1))
@blog_app.route("/author/<user_id>/<int:count>/<int:page>/")
def posts_by_author(user_id, count, page):
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    config = blogging_engine.config

    meta = _get_meta(storage, count, page, user_id=user_id)
    offset = meta["offset"]

    posts = storage.get_posts(count=count, offset=offset, user_id=user_id,
                              include_draft=False, tag=None, recent=True)
    render = config.get("RENDER_TEXT", True)
    if len(posts):
        for post in posts:
            _process_post(post, blogging_engine, render=render)
    else:
        flash("No posts found for this user!", "warning")
    return render_template("blog/index.html", posts=posts, meta=meta,
                           config=config)


@blog_app.route('/editor/', methods=["GET", "POST"],
                defaults={"post_id": None})
@blog_app.route('/editor/<int:post_id>/', methods=["GET", "POST"])
@login_required
def editor(post_id):
    blogging_engine = _get_blogging_engine(current_app)
    post_processor = blogging_engine.post_processor
    config = blogging_engine.config
    storage = blogging_engine.storage
    if request.method == 'POST':
        form = BlogEditor(request.form)
        if form.validate():
            post = storage.get_post_by_id(post_id)
            if (post is not None) and \
                    (current_user.get_id() == post["user_id"]) and \
                    (post["post_id"] == post_id):
                pass
            else:
                post = {}
            pid = _store_form_data(form, storage, current_user, post)
            flash("Blog posted successfully!", "info")
            slug = post_processor.create_slug(form.title.data)
            return redirect(url_for("blog_app.page_by_id", post_id=pid,
                                    slug=slug))
        else:
            flash("There were errors in the blog submission", "warning")
            return render_template("blog/editor.html", form=form,
                                   post_id=post_id, config=config)
    else:
        if post_id is not None:
            post = storage.get_post_by_id(post_id)
            if (post is not None) and \
                    (current_user.get_id() == post["user_id"]):
                tags = ", ".join(post["tags"])
                form = BlogEditor(title=post["title"], text=post["text"],
                                  tags=tags)
                return render_template("blog/editor.html", form=form,
                                       post_id=post_id, config=config)
            else:
                flash("You do not have the rights to edit this post",
                      "warning")
                return redirect(url_for("blog_app.editor", post_id=None))

    form = BlogEditor()
    return render_template("blog/editor.html", form=form, post_id=post_id,
                           config=config)


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


@blog_app.route("/sitemap.xml")
def sitemap():
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    config = blogging_engine.config
    posts = storage.get_posts(count=None, offset=None, recent=True,
                              user_id=None, tag=None, include_draft=False)
    for post in posts:
        _process_post(post, blogging_engine, render=False)
    sitemap_xml = render_template("blog/sitemap.xml", posts=posts,
                                  config=config)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


@blog_app.route('/feeds/all.atom.xml')
def recent_feed():
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    config = blogging_engine.config
    posts = storage.get_posts(count=None, offset=None, recent=True,
                              user_id=None, tag=None, include_draft=False)
    feed = AtomFeed(
        '%s - All Articles' % config.get("SITENAME", "Flask-Blogging"),
        feed_url=request.url, url=request.url_root, generator=None)

    for post in posts:
        _process_post(post, blogging_engine, render=True)
        feed.add(post["title"], unicode(post["rendered_text"]),
                 content_type='html',
                 author=post["user_name"],
                 url=config.get("SITEURL", "")+post["url"],
                 updated=post["last_modified_date"],
                 published=post["post_date"])
    response = feed.get_response()
    response.headers["Content-Type"] = "application/xml"
    return response
