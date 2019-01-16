from flask import Flask, render_template_string, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user
from flask_blogging import SQLAStorage, BloggingEngine
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<User %r>' % self.username
     
    def get_name(self):
        return self.username


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"  # for WTF-forms and login
app.config["BLOGGING_URL_PREFIX"] = "/blog"
app.config["BLOGGING_DISQUS_SITENAME"] = "test"
app.config["BLOGGING_SITEURL"] = "http://localhost:8000"
app.config["BLOGGING_SITENAME"] = "My Site"
app.config["FILEUPLOAD_LOCALSTORAGE_IMG_FOLDER"] = "fileupload"
app.config["FILEUPLOAD_PREFIX"] = "/fileupload"
app.config["FILEUPLOAD_ALLOWED_EXTENSIONS"] = ["png", "jpg", "jpeg", "gif"]
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:////tmp/blog.db'
db.init_app(app)

with app.app_context():
    # extensions
    sql_storage = SQLAStorage(db=db)
    login_manager = LoginManager(app)
    db.create_all()
    # create test user if not exists
    user = User.query.filter_by(username="testuser").first()
    if user is None:
        user = User("testuser", email="testuser2@gmail.com")
        db.session.add(user)
        db.session.commit()
blog_engine = BloggingEngine(app, sql_storage)
admin = Admin(app, name="Flask-Blogging", template_mode='bootstrap3')
Post = sql_storage.post_model
Tag = sql_storage.tag_model
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Tag, db.session))
admin.add_view(ModelView(User, db.session))

@login_manager.user_loader
@blog_engine.user_loader
def load_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    print (user_id, user.get_name())
    return user

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
        &nbsp&nbsp<a href="/fileupload/">FileUpload</a>
        &nbsp&nbsp<a href="/admin/">Admin</a>
    </body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(index_template)

@app.route("/login/")
def login():
    user = User.query.filter_by(username="testuser").first()
    login_user(user)
    return redirect("/blog")

@app.route("/logout/")
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    
    app.run(debug=True, port=8000, use_reloader=True)
