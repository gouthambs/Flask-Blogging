try:
    from builtins import object
except ImportError:
    pass
import markdown
from markdown.extensions.meta import MetaExtension
from flask import url_for
from flask_login import current_user
from slugify import slugify


class MathJaxPattern(markdown.inlinepatterns.Pattern):

    def __init__(self):
        markdown.inlinepatterns.Pattern.__init__(self,
                                                 r'(?<!\\)(\$\$?)(.+?)\2')

    def handleMatch(self, m):
        node = markdown.util.etree.Element('mathjax')
        node.text = markdown.util.AtomicString(m.group(2) + m.group(3) +
                                               m.group(2))
        return node


class MathJaxExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        # Needs to come before escape matching because \ is pretty important
        # in LaTeX
        md.inlinePatterns.add('mathjax', MathJaxPattern(), '<escape')


def makeExtension(configs=[]):
    return MathJaxExtension(configs)


class PostProcessor(object):

    _markdown_extensions = [MathJaxExtension(), MetaExtension()]

    @staticmethod
    def create_slug(title):
        return slugify(title)

    @classmethod
    def construct_url(cls, post):
        url = url_for("blogging.page_by_id", post_id=post["post_id"],
                      slug=cls.create_slug(post["title"]))
        return url

    @classmethod
    def render_text(cls, post):
        md = markdown.Markdown(extensions=cls.all_extensions())
        post["rendered_text"] = md.convert(post["text"])
        post["meta"] = md.Meta

    @classmethod
    def is_author(cls, post, user):
        return user.get_id() == u''+str(post['user_id'])

    @classmethod
    def process(cls, post, render=True):
        """
        This method takes the post data and renders it
        :param post:
        :param render:
        :return:
        """
        post["slug"] = cls.create_slug(post["title"])
        post["editable"] = cls.is_author(post, current_user)
        post["url"] = cls.construct_url(post)
        post["priority"] = 0.8
        if render:
            cls.render_text(post)

    @classmethod
    def all_extensions(cls):
        return cls._markdown_extensions

    @classmethod
    def set_custom_extensions(cls, extensions):
        if type(extensions) == list:
            cls._markdown_extensions.extend(extensions)
