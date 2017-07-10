import os
import shutil
import tempfile
from test import FlaskBloggingTestCase
from flask_blogging.filestorage import FileStorage

class TestFileStorage(FlaskBloggingTestCase):
    def _create_storage(self):
        temp_dir = os.path.join(tempfile.gettempdir(),"test_blog_storage")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.mkdir(temp_dir)
        self._blog_dir = temp_dir
        self.storage = FileStorage(temp_dir)

    def setUp(self):
        FlaskBloggingTestCase.setUp(self)
        self._create_storage()

    def tearDown(self):
        shutil.rmtree(self._blog_dir)

    def test_dir_structure(self):
        self.assertTrue(os.path.exists(os.path.join(self._blog_dir, "posts")),
                        "posts dir missing")
        self.assertTrue(os.path.exists(os.path.join(self._blog_dir, "trash")),
                        "trash dir missing")
        self.assertTrue(os.path.exists(os.path.join(self._blog_dir, "post_index")),
                        "post_index missing")
        self.assertTrue(os.path.exists(os.path.join(self._blog_dir, "author_index")),
                        "author_index missing")
        self.assertTrue(os.path.exists(os.path.join(self._blog_dir, "tag_index")),
                        "tag_index missing")


