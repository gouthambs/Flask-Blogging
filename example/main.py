from flask import Flask
import os
import tempfile
from sqlalchemy import create_engine
from flask_blogging import SQLAStorage, BloggingEngine
from flask.ext.login import UserMixin, LoginManager, login_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"

# extensions
db_dir = os.path.join(tempfile.gettempdir(), "temp.db")
engine = create_engine('sqlite:///'+db_dir)
sql_storage = SQLAStorage(engine)
blog_engine = BloggingEngine(app, sql_storage, config={'site_name': "My Site"})
login_manager = LoginManager(app)


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    def get_name(self):
        return "User "+self.id

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
    user = User("newuser")
    login_user(user)


if __name__ == "__main__":
    try:
        app.run(debug=True, port=9000, use_reloader=True)
    except KeyboardInterrupt:
        os.remove(db_dir)