import markdown
from markdown.extensions.meta import MetaExtension
from flask import url_for


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
