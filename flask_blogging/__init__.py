__author__ = 'Gouthaman Balaraman'
__version__ = '0.1.0'

import markdown
from markdown.extensions.meta import MetaExtension
from flask import url_for

class BloggingEngine(object):
    def __init__(self, app=None, storage=None, url_prefix="/blog", post_processor=None):
        """
        Creates the instance

        :param app: Optional app to use
        :param storage: The storage pertaining to the storage of choice.
        :return:
        """
        self.app = None
        self.storage = None
        self.url_prefix = url_prefix
        self.post_processor = PostProcessor() if post_processor is None else post_processor
        if app is not None and storage is not None:
            self.init_app(app, storage)

    def init_app(self, app, storage):
        self.app = app
        self.storage = storage
        #self.app.config["FLASK_BLOGGING_STORAGE"] = self.storage
        from flask_blogging.views import blog_app
        self.app.register_blueprint(blog_app, url_prefix=self.url_prefix)
        self.app.extensions["FLASK_BLOGGING_ENGINE"] = self


class Storage(object):

    def save_post(self, title, text, user_id, tags, draft=False, post_id=None):
        """
        Persist the blog post data
        :param title:
        :type title: str
        :param text:
        :param user_id:
        :param tags:
        :param draft:
        :param post_id:
        :return: The post_id value, in case of insert or update
        """
        raise NotImplementedError("This method needs to be implemented by the inheriting class")

    def get_post_by_id(self, post_id):
        """
        Fetch the blog post given by post_id
        :param post_id: the identifier for the blog post
        :type post_id: int
        :return:
        """
        raise NotImplementedError("This method needs to be implemented by the inheriting class")

    def get_posts(self, count=10, offset=0, recent=True,  tag=None, user_id=None):
        """
        Get posts given by filter criteria
        :param count:
        :param offset:
        :param recent:
        :param tag:
        :param user_id:
        :return:
        """
        raise NotImplementedError("This method needs to be implemented by the inheriting class")

    @staticmethod
    def normalize_tags(tags):
        return [tag.upper() for tag in tags]


class MathJaxPattern(markdown.inlinepatterns.Pattern):

    def __init__(self):
        markdown.inlinepatterns.Pattern.__init__(self, r'(?<!\\)(\$\$?)(.+?)\2')

    def handleMatch(self, m):
        node = markdown.util.etree.Element('mathjax')
        node.text = markdown.util.AtomicString(m.group(2) + m.group(3) + m.group(2))
        return node

class MathJaxExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        # Needs to come before escape matching because \ is pretty important in LaTeX
        md.inlinePatterns.add('mathjax', MathJaxPattern(), '<escape')

def makeExtension(configs=[]):
    return MathJaxExtension(configs)


class PostProcessor(object):

    markdown_extensions = [MathJaxExtension(), MetaExtension()]

    @staticmethod
    def create_slug(title):
        return "-".join([t.lower() for t in title.split()])

    @classmethod
    def construct_url(cls, post):
        url = url_for("blog_app.page_by_id", post_id=post["post_id"], slug=cls.create_slug(post["title"]))
        return url

    @classmethod
    def render_text(cls, post):
        md = markdown.Markdown(extensions=cls.markdown_extensions)
        post["rendered_text"] = md.convert(post["text"])
        post["meta"] = md.Meta

    @classmethod
    def process(cls, post, render=True):
        post["url"] = cls.construct_url(post)
        if render:
            cls.render_text(post)
        return
