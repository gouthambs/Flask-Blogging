from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_blogging import SQLAStorage, BloggingEngine
from flask.ext.login import AnonymousUserMixin, LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:\\temp.db'
app.config["SECRET_KEY"] = "secret"

# extensions
db = SQLAlchemy(app)
sqla = SQLAStorage(db.engine)
blog_engine = BloggingEngine(app, sqla, config={'site_name': "My Site"})
login_manager = LoginManager(app)



@app.route("/", methods=["GET"])
def index():
    return "Hello World!"


class User(AnonymousUserMixin):
    def __init__(self, user_id):
        self.user_id = user_id

    def get_name(self):
        return "User "+self.user_id

@login_manager.user_loader
@blog_engine.user_loader
def load_user(user_id):
    return User(user_id)

sample_text = """
# An exhibit of Markdown

This note demonstrates some of what [Markdown][1] is capable of doing.
Inline math like $\\alpha_i$ would work. Blocks
$$ \\alpha=\\beta$$
work as well.
"""

@app.before_first_request
def add_posts():
    for i in range(20):
        tags = ["hello"] if i < 10 else ["world"]
        user = "testuser" if i<10 else "newuser"
        blog_engine.storage.save_post(title="Sample Title%d" % i, text=sample_text, user_id=user, tags=tags)


if __name__ == "__main__":
    import logging
    import sys
    app_logger = logging.getLogger("flask-blogging")
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setLevel(logging.DEBUG)
    app_logger.addHandler(log_handler)
    app_logger.setLevel(logging.DEBUG)
    app.run(debug=True, port=9000, use_reloader=True)
