from flask import Flask, render_template_string, redirect
from flask_login import UserMixin, LoginManager, login_user, logout_user
from flask_blogging import SQLAStorage, BloggingEngine
from flask_blogging.gcdatastore import GoogleCloudDatastore
from flask_fileupload.storage.gcstorage import GoogleCloudStorage
from flask_fileupload import FlaskFileUpload
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/credentials.json"

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"  # for WTF-forms and login
app.config["BLOGGING_URL_PREFIX"] = "/blog"
app.config["BLOGGING_DISQUS_SITENAME"] = "test"
app.config["BLOGGING_SITEURL"] = "http://localhost:8000"
app.config["BLOGGING_SITENAME"] = "My Site"
app.config["BLOGGING_TWITTER_USERNAME"] = "@me"
app.config["BLOGGING_ALLOW_FILEUPLOAD"] = True
app.config["FILEUPLOAD_LOCALSTORAGE_IMG_FOLDER"] = "fileupload"
app.config["FILEUPLOAD_PREFIX"] = "/fileupload"
app.config["FILEUPLOAD_ALLOWED_EXTENSIONS"] = ["png", "jpg", "jpeg", "gif"]

# extensions

"""Google Cloud Storage configuration docs:
   https://github.com/Speedy1991/Flask-FileUpload/tree/master/doc/google_cloud_storage.md
"""
gcstorage = GoogleCloudStorage(app)
file_upload = FlaskFileUpload(app, storage=gcstorage)

gc_datastore = GoogleCloudDatastore()
blog_engine = BloggingEngine(app, gc_datastore, file_upload=file_upload)
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
        &nbsp&nbsp<a href="/fileupload/">FileUpload</a>
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
    app.run(debug=True, port=8000, use_reloader=True)
