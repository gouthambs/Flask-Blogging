"""
This example demonstrates the use of caches
"""
from flask import Flask, render_template_string, redirect, current_app
from sqlalchemy import create_engine, MetaData
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
from flask_blogging import SQLAStorage, BloggingEngine
from flask_principal import identity_changed, Identity, AnonymousIdentity, identity_loaded, \
    UserNeed, RoleNeed
from flask_cache import Cache


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"  # for WTF-forms and login
app.config["BLOGGING_URL_PREFIX"] = "/blog"
app.config["BLOGGING_DISQUS_SITENAME"] = "test"
app.config["BLOGGING_SITEURL"] = "http://localhost:8000"
app.config["BLOGGING_SITENAME"] = "My Site"
app.config["BLOGGING_PERMISSIONS"] = False  # Enable blogger permissions'
app.config["CACHE_TYPE"] = "simple"

# create cache
cache = Cache(app)

# extensions
engine = create_engine('sqlite:////tmp/blog.db')
meta = MetaData()
sql_storage = SQLAStorage(engine, metadata=meta)
blog_engine = BloggingEngine(app, sql_storage, cache=cache)
login_manager = LoginManager(app)
meta.create_all(bind=engine)

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    def get_name(self):
        return "Paul Dirac"  # typically the user's name


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user
    if hasattr(current_user, "id"):
        identity.provides.add(UserNeed(current_user.id))
    identity.provides.add(RoleNeed("blogger"))


@login_manager.user_loader
@blog_engine.user_loader
def load_user(user_id):
    return User(user_id)

index_template = """
<!DOCTYPE html>
<html>
    <head> </head>
    <body>
        {% if current_user.is_authenticated %}
            <a href="/logout/"> Logout </a>
        {% else %}
            <a href="/login/"> Login </a>
        {% endif %}
        &nbsp&nbsp<a href="/blog/"> Blog </a>
        &nbsp&nbsp<a href="/blog/sitemap.xml">Sitemap</a>
        &nbsp&nbsp<a href="/blog/feeds/all.atom.xml">ATOM</a>
    </body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(index_template)

@app.route("/login/")
def login():
    user = User("testuser")
    login_user(user)

    # notify the change of role
    identity_changed.send(current_app._get_current_object(),
                          identity=Identity("testuser"))
    return redirect("/blog")

@app.route("/logout/")
def logout():
    logout_user()

    # notify the change of role
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=8000, use_reloader=True)
