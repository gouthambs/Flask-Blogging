from __future__ import division
try:
    from builtins import str
except ImportError:
    pass
from .processor import PostProcessor
from flask_login import login_required, current_user
from flask import Blueprint, current_app, render_template, request, redirect, \
    url_for, flash, make_response
from flask_blogging.forms import BlogEditor
import math
from werkzeug.contrib.atom import AtomFeed
import datetime
from flask_principal import PermissionDenied
from .signals import page_by_id_fetched, page_by_id_processed, \
    posts_by_tag_fetched, posts_by_tag_processed, \
    posts_by_author_fetched, posts_by_author_processed, \
    index_posts_fetched, index_posts_processed, \
    feed_posts_fetched, feed_posts_processed, \
    sitemap_posts_fetched, sitemap_posts_processed, editor_post_saved, \
    post_deleted, editor_get_fetched
from .utils import ensureUtf


def _get_blogging_engine(app):
    return app.extensions["FLASK_BLOGGING_ENGINE"]


def _get_user_name(user):
    user_name = user.get_name() if hasattr(user, "get_name") else str(user)
    return user_name


def _clear_cache(cache):
    cache.delete_memoized(index)
    cache.delete_memoized(page_by_id)
    cache.delete_memoized(posts_by_author)
    cache.delete_memoized(posts_by_tag)
    cache.delete_memoized(sitemap)
    cache.delete_memoized(feed)


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
    pid = storage.save_post(title, text, user_id, tags, draft=draft,
                            post_date=post_date,
                            last_modified_date=last_modified_date,
                            post_id=post_id)
    return pid


def _get_meta(storage, count, page, tag=None, user_id=None):
    max_posts = storage.count_posts(tag=tag, user_id=user_id)
    max_pages = math.ceil(float(max_posts)/float(count))
    max_offset = (max_pages-1)*count
    offset = min(max(0, (page-1)*count), max_offset)
    if (tag is None) and (user_id is None):
        prev_page = None if page <= 1 else url_for(
            "blogging.index", count=count, page=page-1)
        next_page = None if page >= max_pages else url_for(
            "blogging.index", count=count, page=page+1)
    elif tag:
        prev_page = None if page <= 1 else url_for(
            "blogging.posts_by_tag", tag=tag, count=count, page=page-1)
        next_page = None if page >= max_pages else url_for(
            "blogging.posts_by_tag", tag=tag, count=count, page=page+1)
    elif user_id:
        prev_page = None if page <= 1 else url_for(
            "blogging.posts_by_author", user_id=user_id, count=count,
            page=page-1)
        next_page = None if page >= max_pages else url_for(
            "blogging.posts_by_author", user_id=user_id, count=count,
            page=page+1)
    else:
        prev_page = next_page = None

    pagination = dict(prev_page=prev_page, next_page=next_page)
    meta = dict(max_posts=max_posts, max_pages=max_pages, page=page,
                max_offset=max_offset, offset=offset, count=count,
                pagination=pagination)
    return meta


def _is_blogger(blogger_permission):
    authenticated = current_user.is_authenticated() if \
        callable(current_user.is_authenticated) \
        else current_user.is_authenticated
    is_blogger = authenticated and \
        blogger_permission.require().can()
    return is_blogger


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
    count = count or config.get("BLOGGING_POSTS_PER_PAGE", 10)

    meta = _get_meta(storage, count, page)
    offset = meta["offset"]
    meta["is_user_blogger"] = _is_blogger(blogging_engine.blogger_permission)
    meta["count"] = count
    meta["page"] = page

    render = config.get("BLOGGING_RENDER_TEXT", True)
    posts = storage.get_posts(count=count, offset=offset, include_draft=False,
                              tag=None, user_id=None, recent=True)
    index_posts_fetched.send(blogging_engine.app, engine=blogging_engine,
                             posts=posts, meta=meta)
    for post in posts:
        blogging_engine.process_post(post, render=render)
    index_posts_processed.send(blogging_engine.app, engine=blogging_engine,
                               posts=posts, meta=meta)
    return render_template("blogging/index.html", posts=posts, meta=meta,
                           config=config)


def page_by_id(post_id, slug):
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    config = blogging_engine.config
    post = storage.get_post_by_id(post_id)
    meta = {}
    meta["is_user_blogger"] = _is_blogger(blogging_engine.blogger_permission)

    render = config.get("BLOGGING_RENDER_TEXT", True)
    meta["post_id"] = post_id
    meta["slug"] = slug
    page_by_id_fetched.send(blogging_engine.app, engine=blogging_engine,
                            post=post, meta=meta)
    if post is not None:
        blogging_engine.process_post(post, render=render)
        page_by_id_processed.send(blogging_engine.app, engine=blogging_engine,
                                  post=post, meta=meta)
        return render_template("blogging/page.html", post=post, config=config,
                               meta=meta)
    else:
        flash("The page you are trying to access is not valid!", "warning")
        return redirect(url_for("blogging.index"))


def posts_by_tag(tag, count, page):
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    config = blogging_engine.config
    count = count or config.get("BLOGGING_POSTS_PER_PAGE", 10)
    meta = _get_meta(storage, count, page, tag=tag)
    offset = meta["offset"]
    meta["is_user_blogger"] = _is_blogger(blogging_engine.blogger_permission)
    meta["tag"] = tag
    meta["count"] = count
    meta["page"] = page
    render = config.get("BLOGGING_RENDER_TEXT", True)
    posts = storage.get_posts(count=count, offset=offset, tag=tag,
                              include_draft=False, user_id=None, recent=True)
    posts_by_tag_fetched.send(blogging_engine.app, engine=blogging_engine,
                              posts=posts, meta=meta)
    if len(posts):
        for post in posts:
            blogging_engine.process_post(post, render=render)
        posts_by_tag_processed.send(blogging_engine.app,
                                    engine=blogging_engine,
                                    posts=posts, meta=meta)
        return render_template("blogging/index.html", posts=posts, meta=meta,
                               config=config)
    else:
        flash("No posts found for this tag!", "warning")
        return redirect(url_for("blogging.index", post_id=None))


def posts_by_author(user_id, count, page):
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    config = blogging_engine.config
    count = count or config.get("BLOGGING_POSTS_PER_PAGE", 10)
    meta = _get_meta(storage, count, page, user_id=user_id)
    offset = meta["offset"]
    meta["is_user_blogger"] = _is_blogger(blogging_engine.blogger_permission)
    meta["user_id"] = user_id
    meta["count"] = count
    meta["page"] = page

    posts = storage.get_posts(count=count, offset=offset, user_id=user_id,
                              include_draft=False, tag=None, recent=True)
    render = config.get("BLOGGING_RENDER_TEXT", True)
    posts_by_author_fetched.send(blogging_engine.app, engine=blogging_engine,
                                 posts=posts, meta=meta)
    if len(posts):
        for post in posts:
            blogging_engine.process_post(post, render=render)
        posts_by_author_processed.send(blogging_engine.app,
                                       engine=blogging_engine, posts=posts,
                                       meta=meta)
        return render_template("blogging/index.html", posts=posts, meta=meta,
                               config=config)
    else:
        flash("No posts found for this user!", "warning")
        return redirect(url_for("blogging.index", post_id=None))


@login_required
def editor(post_id):
    blogging_engine = _get_blogging_engine(current_app)
    cache = blogging_engine.cache
    if cache:
        _clear_cache(cache)
    try:
        with blogging_engine.blogger_permission.require():
            post_processor = blogging_engine.post_processor
            config = blogging_engine.config
            storage = blogging_engine.storage
            if request.method == 'POST':
                form = BlogEditor(request.form)
                if form.validate():
                    post = storage.get_post_by_id(post_id)
                    if (post is not None) and \
                            (PostProcessor.is_author(post, current_user)) and \
                            (post["post_id"] == post_id):
                        pass
                    else:
                        post = {}
                    pid = _store_form_data(form, storage, current_user, post)
                    editor_post_saved.send(blogging_engine.app,
                                           engine=blogging_engine,
                                           post_id=pid,
                                           user=current_user,
                                           post=post)
                    flash("Blog posted successfully!", "info")
                    slug = post_processor.create_slug(form.title.data)
                    return redirect(url_for("blogging.page_by_id", post_id=pid,
                                            slug=slug))
                else:
                    flash("There were errors in blog submission", "warning")
                    return render_template("blogging/editor.html", form=form,
                                           post_id=post_id, config=config)
            else:
                if post_id is not None:
                    post = storage.get_post_by_id(post_id)
                    if (post is not None) and \
                            (PostProcessor.is_author(post, current_user)):
                        tags = ", ".join(post["tags"])
                        form = BlogEditor(title=post["title"],
                                          text=post["text"], tags=tags)
                        editor_get_fetched.send(blogging_engine.app,
                                                engine=blogging_engine,
                                                post_id=post_id,
                                                form=form)
                        return render_template("blogging/editor.html",
                                               form=form, post_id=post_id,
                                               config=config)
                    else:
                        flash("You do not have the rights to edit this post",
                              "warning")
                        return redirect(url_for("blogging.index",
                                                post_id=None))

            form = BlogEditor()
            return render_template("blogging/editor.html", form=form,
                                   post_id=post_id, config=config)
    except PermissionDenied:
        flash("You do not have permissions to create or edit posts", "warning")
        return redirect(url_for("blogging.index", post_id=None))


@login_required
def delete(post_id):
    blogging_engine = _get_blogging_engine(current_app)
    cache = blogging_engine.cache
    if cache:
        _clear_cache(cache)
    try:
        with blogging_engine.blogger_permission.require():
            storage = blogging_engine.storage
            post = storage.get_post_by_id(post_id)
            if (post is not None) and \
                    (PostProcessor.is_author(post, current_user)):
                success = storage.delete_post(post_id)
                if success:
                    flash("Your post was successfully deleted", "info")
                    post_deleted.send(blogging_engine.app,
                                      engine=blogging_engine,
                                      post_id=post_id,
                                      post=post)
                else:
                    flash("There were errors while deleting your post",
                          "warning")
            else:
                flash("You do not have the rights to delete this post",
                      "warning")
            return redirect(url_for("blogging.index"))
    except PermissionDenied:
        flash("You do not have permissions to delete posts", "warning")
        return redirect(url_for("blogging.index", post_id=None))


def sitemap():
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    config = blogging_engine.config
    posts = storage.get_posts(count=None, offset=None, recent=True,
                              user_id=None, tag=None, include_draft=False)
    sitemap_posts_fetched.send(blogging_engine.app, engine=blogging_engine,
                               posts=posts)

    if len(posts):
        for post in posts:
            blogging_engine.process_post(post, render=False)
        sitemap_posts_processed.send(blogging_engine.app,
                                     engine=blogging_engine, posts=posts)
    sitemap_xml = render_template("blogging/sitemap.xml", posts=posts,
                                  config=config)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


def feed():
    blogging_engine = _get_blogging_engine(current_app)
    storage = blogging_engine.storage
    config = blogging_engine.config
    count = config.get("BLOGGING_FEED_LIMIT")
    posts = storage.get_posts(count=count, offset=None, recent=True,
                              user_id=None, tag=None, include_draft=False)

    feed = AtomFeed(
        '%s - All Articles' % config.get("BLOGGING_SITENAME",
                                         "Flask-Blogging"),
        feed_url=request.url, url=request.url_root, generator=None)

    feed_posts_fetched.send(blogging_engine.app, engine=blogging_engine,
                            posts=posts)
    if len(posts):
        for post in posts:
            blogging_engine.process_post(post, render=True)
            feed.add(post["title"], ensureUtf(post["rendered_text"]),
                     content_type='html',
                     author=post["user_name"],
                     url=config.get("BLOGGING_SITEURL", "")+post["url"],
                     updated=post["last_modified_date"],
                     published=post["post_date"])
        feed_posts_processed.send(blogging_engine.app, engine=blogging_engine,
                                  feed=feed)
    response = feed.get_response()
    response.headers["Content-Type"] = "application/xml"
    return response


def unless(blogging_engine):
    # disable caching for bloggers. They can change state!
    def _unless():
        return _is_blogger(blogging_engine.blogger_permission)
    return _unless


def cached_func(blogging_engine, func):
    cache = blogging_engine.cache
    if cache is None:
        return func
    else:
        unless_func = unless(blogging_engine)
        config = blogging_engine.config
        cache_timeout = config.get("BLOGGING_CACHE_TIMEOUT", 60)  # 60 seconds
        memoized_func = cache.memoize(
            timeout=cache_timeout, unless=unless_func)(func)
        return memoized_func


def create_blueprint(import_name, blogging_engine):

    blog_app = Blueprint("blogging", import_name, template_folder='templates')

    # register index
    index_func = cached_func(blogging_engine, index)
    blog_app.add_url_rule("/", defaults={"count": None, "page": 1},
                          view_func=index_func)
    blog_app.add_url_rule("/<int:count>/", defaults={"page": 1},
                          view_func=index_func)
    blog_app.add_url_rule("/<int:count>/<int:page>/", view_func=index_func)

    # register page_by_id
    page_by_id_func = cached_func(blogging_engine, page_by_id)
    blog_app.add_url_rule("/page/<int:post_id>/", defaults={"slug": ""},
                          view_func=page_by_id_func)
    blog_app.add_url_rule("/page/<int:post_id>/<slug>/",
                          view_func=page_by_id_func)

    # register posts_by_tag
    posts_by_tag_func = cached_func(blogging_engine, posts_by_tag)
    blog_app.add_url_rule("/tag/<tag>/", defaults=dict(count=None, page=1),
                          view_func=posts_by_tag_func)
    blog_app.add_url_rule("/tag/<tag>/<int:count>/", defaults=dict(page=1),
                          view_func=posts_by_tag_func)
    blog_app.add_url_rule("/tag/<tag>/<int:count>/<int:page>/",
                          view_func=posts_by_tag_func)

    # register posts_by_author
    posts_by_author_func = cached_func(blogging_engine, posts_by_author)
    blog_app.add_url_rule("/author/<user_id>/",
                          defaults=dict(count=None, page=1),
                          view_func=posts_by_author_func)
    blog_app.add_url_rule("/author/<user_id>/<int:count>/",
                          defaults=dict(page=1),
                          view_func=posts_by_author_func)
    blog_app.add_url_rule("/author/<user_id>/<int:count>/<int:page>/",
                          view_func=posts_by_author_func)

    # register editor
    editor_func = editor  # For now lets not cache this
    blog_app.add_url_rule('/editor/', methods=["GET", "POST"],
                          defaults={"post_id": None},
                          view_func=editor_func)
    blog_app.add_url_rule('/editor/<int:post_id>/', methods=["GET", "POST"],
                          view_func=editor_func)

    # register delete
    delete_func = delete  # For now lets not cache this
    blog_app.add_url_rule("/delete/<int:post_id>/", methods=["POST"],
                          view_func=delete_func)

    # register sitemap
    sitemap_func = cached_func(blogging_engine, sitemap)
    blog_app.add_url_rule("/sitemap.xml", view_func=sitemap_func)

    # register feed
    feed_func = cached_func(blogging_engine, feed)
    blog_app.add_url_rule('/feeds/all.atom.xml', view_func=feed_func)

    return blog_app
