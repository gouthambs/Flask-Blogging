from flask import Flask, render_template_string, redirect
from flask_login import UserMixin, LoginManager, login_user, logout_user
from flask_blogging import BloggingEngine
from flask_blogging.dynamodbstorage import DynamoDBStorage

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"  # for WTF-forms and login
app.config["BLOGGING_URL_PREFIX"] = "/blog"
app.config["BLOGGING_DISQUS_SITENAME"] = "test"
app.config["BLOGGING_SITEURL"] = ""
app.config["BLOGGING_SITENAME"] = "My Site"
app.config["BLOGGING_ALLOW_FILEUPLOAD"] = False


# extensions
dyn_storage = DynamoDBStorage(endpoint_url='http://localhost:8000')
blog_engine = BloggingEngine(app, dyn_storage)
login_manager = LoginManager(app)

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    def get_name(self):
        return "Paul Dirac"  # typically the user's name

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
    return redirect("/blog")

@app.route("/logout/")
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=8001, use_reloader=True)
