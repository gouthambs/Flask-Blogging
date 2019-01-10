import logging
from .storage import Storage
from google.cloud import datastore
import datetime
from shortuuid import ShortUUID
from operator import itemgetter


class GoogleCloudDatastore(Storage):

    def __init__(self, namespace=None):
        self._logger = logging.getLogger("flask-blogging")
        self._client = datastore.Client(namespace=namespace)

    def _get_new_post_id(self):
        key = self._client.key('PostIDCounter', 'Counter')
        query = self._client.get(key)

        if query:
            counter = dict(query)
        else:
            counter = None

        if counter:
            counter = counter["value"]+1
            key = self._client.key('PostIDCounter', 'Counter')
            task = self._client.get(key)
            task['value'] = counter
            self._client.put(task)

            return int(counter)
        else:
            # Create a new counter
            key = self._client.key('PostIDCounter', 'Counter')
            counter = datastore.Entity(key=key)
            counter.update({
                    'value': 1,
            })
            self._client.put(counter)
            return 1

    def save_post(self, title, text, user_id, tags, draft=False,
                  post_date=None, last_modified_date=None, meta_data=None,
                  post_id=None):
        if post_id is not None:
            update_op = True
        else:
            update_op = False

        post_id = post_id or self._get_new_post_id()
        current_datetime = datetime.datetime.utcnow()
        post_date = post_date or current_datetime
        last_modified_date = last_modified_date or current_datetime
        tags = self.normalize_tags(tags)
        draft = True if draft else False

        if not update_op:
            key = self._client.key('Post', int(post_id))
            post = datastore.Entity(key=key, exclude_from_indexes=['text'])
            post.update({
                    'title': title,
                    'text': text,
                    'user_id': user_id,
                    'tags': tags or [],
                    'draft': draft,
                    'post_date': post_date,
                    'last_modified_date': last_modified_date,
                    'meta_data': meta_data,
                    'post_id': int(post_id)
            })
            self._client.put(post)
            return post_id
        else:
            key = self._client.key('Post', int(post_id))
            post = self._client.get(key)
            if not post:
                post_id = self._get_new_post_id()
                key = self._client.key('Post', int(post_id))
                post = datastore.Entity(key=key, exclude_from_indexes=['text'])
            post.update({
                    'title': title,
                    'text': text,
                    'user_id': user_id,
                    'tags': tags or [],
                    'draft': draft,
                    'post_date': post_date,
                    'last_modified_date': last_modified_date,
                    'meta_data': meta_data,
                    'post_id': int(post_id)
            })
            self._client.put(post)
            return int(post_id)

    def _filter_posts_by_tag(self, tag):
        if not tag:
            return []
        else:
            query = self._client.query(kind='Post')
            query.projection = ['post_id', 'tags']
            proj_result = list(query.fetch())

            proj_result = [dict(entity) for entity in proj_result]
            ids = set()

            for entity in proj_result:
                if entity["tags"] == tag:
                    ids.add(entity["post_id"])

            return list(ids)

    def get_posts(self, count=10, offset=0, recent=True, tag=None,
                  user_id=None, include_draft=False):
        """TODO: implement cursors support, if it will be needed.
           But for the regular blog, it is overhead and
           cost savings are minimal.
        """
        query = self._client.query(kind='Post')

        if tag:
            norm_tag = self.normalize_tag(tag)
            posts_ids = self._filter_posts_by_tag(norm_tag)

            if posts_ids:
                keys = [self._client.key('Post', id) for id in posts_ids]
                posts = self._client.get_multi(keys)
            else:
                posts = []
        else:
            if user_id:
                query.add_filter('user_id', '=', user_id)
            if include_draft:
                query.add_filter('draft', '=', include_draft)
            if recent:
                query.order = ['-post_date']
            posts = list(query.fetch(offset=offset, limit=count))

        if not posts:
            return []

        res = []
        for post in posts:
            p = dict(post)
            res.append(p)

        if tag and recent:
            res = sorted(res, key=itemgetter('post_date'), reverse=True)
        elif tag and not recent:
            res = sorted(res, key=itemgetter('post_date'))

        if tag:
            res = res[offset:offset+count]

        return res

    def count_posts(self, tag=None, user_id=None, include_draft=False):
        query = self._client.query(kind='Post')

        if tag:
            norm_tag = self.normalize_tag(tag)
            query.add_filter('tags', '=', norm_tag)
        if user_id:
            query.add_filter('user_id', '=', user_id)
        if include_draft:
            query.add_filter('draft', '=', include_draft)

        posts = list(query.fetch())
        result = len(posts)

        return result

    def get_post_by_id(self, post_id):
        if post_id:
            query = self._client.query(kind='Post')
            query.add_filter('post_id', '=', int(post_id))
            post = list(query.fetch())

            if post:
                res = dict(post[0])
                return res

        return None

    def delete_post(self, post_id):
        if post_id:
            key = self._client.key('Post', int(post_id))

            try:
                self._client.delete(key)
            except Exception as ex:
                self._logger.error(str(ex))
                return False

            return True
        else:
            return False
