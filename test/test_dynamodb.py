try:
    from builtins import range
except ImportError:
    pass
import unittest
from test import FlaskBloggingTestCase
try:
    import boto3
    from flask_blogging.dynamodbstorage import DynamoDBStorage
    HAS_DYNAMODB = True
except ImportError:
    HAS_DYNAMODB = False
import time


@unittest.skipUnless(HAS_DYNAMODB, "Need DynamoDB client to run this test.")
class TestDynamoDBStorage(FlaskBloggingTestCase):

    def _create_storage(self):
        self.storage = DynamoDBStorage(table_prefix="test_",
                                       endpoint_url='http://localhost:8000')

    def setUp(self):
        FlaskBloggingTestCase.setUp(self)
        self._create_storage()

    def tearDown(self):
        self.storage._client.delete_table(TableName='test_blog_posts')
        self.storage._client.delete_table(TableName='test_tag_posts')

    def test_table_exists(self):
        response = self.storage._client.list_tables()
        tables = response["TableNames"]
        self.assertTrue('test_blog_posts' in tables)
        self.assertTrue('test_tag_posts' in tables)

    def test_user_post_table_consistency(self):
        # check if the user post table updates the user_id
        user_id = 1
        post_id = 5
        pid = self.storage.save_post(title="Title", text="Sample Text",
                                     user_id="user", tags=["hello", "world"])
        posts = self.storage.get_posts()
        self.assertEqual(len(posts), 1)
        self.storage.save_post(title="Title", text="Sample Text",
                               user_id="newuser", tags=["hello", "world"],
                               post_id=pid)
        self.assertEqual(len(posts), 1)
        return

    def test_user_post_model_consistency(self):
        # check if the user post table updates the user_id
        user_id = 1
        post_id = 5
        pid = self.storage.save_post(title="Title", text="Sample Text",
                                     user_id="user", tags=["hello", "world"])
        response = self.storage._blog_posts_table.scan()
        posts = response["Items"]
        self.assertEqual(len(posts), 1)
        post = posts[0]
        self.assertEqual(post['title'], "Title")
        self.assertEqual(post['text'], "Sample Text")
        self.assertEqual(post['post_id'], pid)
        return

    def test_tags_consistency(self):
        # check that when tag is updated, the posts get updated
        tags = ["hello", "world"]
        pid = self.storage.save_post(title="Title", text="Sample Text",
                                     user_id="user", tags=tags)
        post = self.storage.get_post_by_id(pid)
        self.assertEqual(len(post["tags"]), 2)
        tags.pop()
        pid = self.storage.save_post(title="Title", text="Sample Text",
                                     user_id="user", tags=tags, post_id=pid)
        post = self.storage.get_post_by_id(pid)
        self.assertEqual(len(post["tags"]), 1)

    def test_save_post(self):
        pid = self.storage.save_post(title="Title1", text="Sample Text",
                                     user_id="testuser",
                                     tags=["hello", "world"])
        pid = self.storage.save_post(title="Title1", text="Sample Text",
                                     user_id="testuser",
                                     tags=["hello", "world"], post_id='1')
        p = self.storage.get_post_by_id('2')
        self.assertIsNone(p)

        # invalid post_id will be treated as inserts
        pid = self.storage.save_post(title="Title1", text="Sample Text",
                                     user_id="testuser",
                                     tags=["hello", "world"],
                                     post_id='5')
        self.assertNotEqual(pid, '5')
        p = self.storage.get_post_by_id(pid)
        self.assertIsNotNone(p)

    def test_delete_post(self):
        # insert, check exists, delete, check doesn't exist anymore
        pid = self.storage.save_post(title="Title1", text="Sample Text",
                                     user_id="testuser",
                                     tags=["hello", "world"])
        p = self.storage.get_post_by_id(pid)
        self.assertIsNotNone(p)
        self.storage.delete_post(pid)
        p = self.storage.get_post_by_id(pid)
        self.assertIsNone(p)

        # insert again.
        pid1 = self.storage.save_post(title="Title1", text="Sample Text",
                                      user_id="testuser",
                                      tags=["hello", "world"],
                                      post_id=pid)
        p = self.storage.get_post_by_id(pid1)
        self.assertNotEqual(pid, pid1)
        self.assertIsNotNone(p)

    def test_get_post_by_id(self):
        pid1 = self.storage.save_post(title="Title1", text="Sample Text1",
                                      user_id="testuser",
                                      tags=["hello", "world"])
        pid2 = self.storage.save_post(title="Title2", text="Sample Text2",
                                      user_id="testuser",
                                      tags=["hello", "my", "world"])

        post = self.storage.get_post_by_id(pid1)
        self._assert_post(post, "Title1", "Sample Text1", "testuser",
                          ["HELLO", "WORLD"])

        post = self.storage.get_post_by_id(pid2)
        self._assert_post(post, "Title2", "Sample Text2", "testuser",
                          ["HELLO", "MY", "WORLD"])

    def _assert_post(self, post, title, text, user_id, tags):
        tags = set([t.upper() for t in tags])
        self.assertSetEqual(set(post["tags"]), tags)
        self.assertEqual(post["title"], title)
        self.assertEqual(post["text"], text)
        self.assertEqual(post["user_id"], user_id)

    def test_get_posts(self):
        self._create_dummy_data()

        # test default queries
        posts = self.storage.get_posts()
        self.assertEqual(len(posts), 10)
        ctr = 19
        for post in posts:
            self._assert_post(post, "Title%d" % ctr,
                              "Sample Text%d" % ctr, "newuser", ["world"])
            ctr -= 1

        posts = self.storage.get_posts(recent=False)
        self.assertEqual(len(posts), 10)
        ctr = 0
        for post in posts:
            self._assert_post(post, "Title%d" % ctr,
                              "Sample Text%d" % ctr, "testuser", ["hello"])
            ctr += 1

        # test count and offset
        posts = self.storage.get_posts(count=5, offset=5, recent=False)
        self.assertEqual(len(posts), 5)
        ctr = 5
        for post in posts:
            self._assert_post(post, "Title%d" % ctr,
                              "Sample Text%d" % ctr, "testuser", ["hello"])
            ctr += 1

        # test tag feature
        posts = self.storage.get_posts(tag="hello", recent=False)
        self.assertEqual(len(posts), 10)
        ctr = 0
        for post in posts:
            self._assert_post(post, "Title%d" % ctr,
                              "Sample Text%d" % ctr, "testuser", ["hello"])
            ctr += 1
        posts = self.storage.get_posts(tag="world", recent=False)
        self.assertEqual(len(posts), 10)
        ctr = 10
        for post in posts:
            self._assert_post(post, "Title%d" % ctr,
                              "Sample Text%d" % ctr, "newuser", ["world"])
            ctr += 1

        # test user_id feature
        posts = self.storage.get_posts(user_id="newuser", recent=True)
        self.assertEqual(len(posts), 10)
        ctr = 19
        for post in posts:
            self._assert_post(post, "Title%d" % ctr,
                              "Sample Text%d" % ctr, "newuser", ["world"])
            ctr -= 1

        posts = self.storage.get_posts(user_id="testuser", recent=True)
        self.assertEqual(len(posts), 10)
        ctr = 9
        for post in posts:
            self._assert_post(post, "Title%d" % ctr,
                              "Sample Text%d" % ctr, "testuser", ["hello"])
            ctr -= 1
        return

    def test_count_posts(self):
        self._create_dummy_data()

        count = self.storage.count_posts()
        self.assertEqual(count, 20)

        # test user
        count = self.storage.count_posts(user_id="testuser")
        self.assertEqual(count, 10)

        count = self.storage.count_posts(user_id="newuser")
        self.assertEqual(count, 10)

        count = self.storage.count_posts(user_id="testuser")
        self.assertEqual(count, 10)

        # test tags
        count = self.storage.count_posts(tag="hello")
        self.assertEqual(count, 10)

        count = self.storage.count_posts(tag="world")
        self.assertEqual(count, 10)

    def _create_dummy_data(self):
        for i in range(20):
            tags = ["hello"] if i < 10 else ["world"]
            user = "testuser" if i < 10 else "newuser"
            self.storage.save_post(title="Title%d" % i,
                                   text="Sample Text%d" % i,
                                   user_id=user, tags=tags)
            time.sleep(0.01)
