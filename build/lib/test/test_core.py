try:
    from builtins import str, range
except ImportError:
    pass

from unittest import TestCase
from flask_blogging import BloggingEngine, PostProcessor
from markdown.extensions.codehilite import CodeHiliteExtension


sample_markdown = """

##This is a test


    :::python
    print("Hello, World")
"""

expected_markup = u'<h2>This is a test</h2>\n' \
                  u'<div class="codehilite"><pre>' \
                  u'<span class="k">print</span>' \
                  u'<span class="p">(</span><span class="s">' \
                  u'&quot;Hello, World&quot;</span><span class="p">)' \
                  u'</span>\n' \
                  u'</pre></div>'


class TestCore(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_custom_md_extension(self):
        extn = CodeHiliteExtension({})
        engine = BloggingEngine(extensions=[extn])
        extns = engine.post_processor.all_extensions()
        self.assertEqual(len(extns), 3)
        self.assertTrue(isinstance(extns[-1], CodeHiliteExtension))
