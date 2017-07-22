import logging
from .storage import Storage
import boto3
from boto3.dynamodb.conditions import Key
import datetime
from shortuuid import ShortUUID
import copy


class DynamoDBStorage(Storage):
    _logger = logging.getLogger("flask-blogging")

    def __init__(self, table_prefix="", region_name=None,
                 endpoint_url=None):
        self._client = boto3.client('dynamodb',
                                    region_name=region_name,
                                    endpoint_url=endpoint_url)
        self._db = boto3.resource("dynamodb",
                                  region_name=region_name,
                                  endpoint_url=endpoint_url)
        self._table_prefix = table_prefix
        self._create_all_tables()
        self._uuid = ShortUUID()
        self._uuid.set_alphabet('23456789abcdefghijkmnopqrstuvwxyz')

    def save_post(self, title, text, user_id, tags, draft=False,
                  post_date=None, last_modified_date=None, meta_data=None,
                  post_id=None):
        try:
            current_datetime = datetime.datetime.utcnow()
            post_date = post_date or current_datetime
            post_date = self._to_timestamp(post_date)
            last_modified_date = last_modified_date or current_datetime
            tags = self.normalize_tags(tags)
            draft = 1 if draft else 0
            r = {'title': title,
                 'text': text,
                 'user_id': user_id,
                 'tags': tags,
                 'draft': draft,
                 'post_date': post_date,
                 'last_modified_date': self._to_timestamp(last_modified_date),
                 'meta_data': meta_data
                 }
            if post_id is not None:
                response = self._blog_posts_table.get_item(
                    Key={'post_id': post_id})
                r0 = response.get("Item")
                post_id = r0['post_id'] if r0 else None

            if post_id is None:
                post_id = self._uuid.uuid()
                r['post_id'] = post_id
                self._blog_posts_table.put_item(Item=r)
                self._insert_tags(tags, post_id, post_date, draft)
            else:
                expr = 'SET title = :title, #t = :text, user_id = :user_id, '\
                       'tags = :tags, draft = :draft, '\
                       'post_date = :post_date, '\
                       'last_modified_date = :last_modified_date, '\
                       'meta_data = :meta_data'
                self._blog_posts_table.update_item(
                    Key={'post_id': post_id},
                    UpdateExpression=expr,
                    ExpressionAttributeValues={
                        ':title': r['title'],
                        ':text': r['text'],
                        ':user_id': r['user_id'],
                        ':tags': r['tags'],
                        ':draft': r['draft'],
                        ':post_date': r['post_date'],
                        ':last_modified_date': r["last_modified_date"],
                        ':meta_data': r['meta_data']
                    },
                    ExpressionAttributeNames={'#t': 'text'},
                    ReturnValues="ALL_NEW"
                )

                tag_inserts = set(r['tags']) - set(r0['tags'])
                tag_deletes = set(r0['tags']) - set(r['tags'])
                self._insert_tags(tag_inserts, post_id, post_date, draft)
                self._delete_tags(tag_deletes, post_id)
        except Exception as e:
            self._logger.exception(str(e))
            post_id = None
        return post_id

    def get_posts(self, count=10, offset=0, recent=True, tag=None,
                  user_id=None, include_draft=False):
        try:
            post_ids = self._get_post_ids(count=count, offset=offset,
                                          recent=recent,
                                          tag=tag, user_id=user_id,
                                          include_draft=include_draft)
        except Exception as e:
            self._logger.exception(str(e))
            post_ids = []
        return [self.get_post_by_id(p) for p in post_ids]

    def _get_post_ids(self, count=10, offset=0, recent=True, tag=None,
                      user_id=None, include_draft=False):
        # include_draft is not supported yet
        kwargs = dict(ProjectionExpression='post_id',
                      ScanIndexForward=not recent)
        if count:
            kwargs['Limit'] = count
        table = self._blog_posts_table
        if user_id:
            kwargs.update(
                dict(IndexName='user_id_index',
                     KeyConditionExpression=Key('user_id').eq(user_id))
            )

        elif tag:
            table = self._tag_posts_table
            norm_tag = self.normalize_tag(tag)
            kwargs.update(
                dict(IndexName='tag_index',
                     KeyConditionExpression=Key('tag').eq(norm_tag))
            )
        else:
            kwargs.update(
                dict(IndexName='post_index',
                     KeyConditionExpression=Key('draft').eq(0))
            )
        if offset and offset > 0:
            kwargs2 = copy.deepcopy(kwargs)
            kwargs2['Limit'] = offset
            response = getattr(table, "query")(**kwargs2)
            last_key = response.get('LastEvaluatedKey')
        else:
            last_key = None

        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        response = getattr(table, "query")(**kwargs)
        return [p['post_id'] for p in response['Items']]

    def count_posts(self, tag=None, user_id=None, include_draft=False):
        try:
            post_ids = self._get_post_ids(count=None, offset=0, tag=tag,
                                          user_id=user_id,
                                          include_draft=include_draft)
            result = len(post_ids)
        except Exception as e:
            self._logger.exception(str(e))
            result = 0
        return result

    def get_post_by_id(self, post_id):
        try:
            response = self._blog_posts_table.get_item(
                Key={'post_id': post_id}
            )
            item = response.get('Item')
            if item:
                r = item
                r['post_date'] = self._from_timestamp(r['post_date'])
                r['last_modified_date'] = \
                    self._from_timestamp(r['last_modified_date'])
                r["draft"] = bool(r["draft"])
            else:
                r = None
        except Exception as e:
            self._logger.exception(str(e))
            r = None
        return r

    def delete_post(self, post_id):
        try:
            r = self.get_post_by_id(post_id)
            if r:
                response = self._blog_posts_table.delete_item(
                    Key={'post_id': post_id})
                self._delete_tags(r["tags"], post_id)
                return True
            else:
                return False
        except Exception as e:
            self._logger.exception(str(e))
            return False

    @staticmethod
    def _to_timestamp(date_time):
        return date_time.isoformat()

    @staticmethod
    def _from_timestamp(timestamp):
        return datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")

    def _table_name(self, table_name):
        return self._table_prefix + table_name

    def _create_all_tables(self):
        response = self._client.list_tables()
        table_names = response["TableNames"]
        self._create_blog_posts_table(table_names)
        self._create_tag_posts_table(table_names)

    def _create_blog_posts_table(self, table_names):
        bp_table_name = self._table_name("blog_posts")
        if bp_table_name not in table_names:
            self._client.create_table(
                TableName=bp_table_name,
                KeySchema=[{
                    'AttributeName': 'post_id',
                    'KeyType': 'HASH'
                }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': "user_id_index",
                        'KeySchema': [
                            {
                                'AttributeName': 'user_id',
                                'KeyType': 'HASH',
                            },
                            {
                                'AttributeName': 'post_date',
                                'KeyType': 'RANGE',
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 2,
                            'WriteCapacityUnits': 2
                        }
                    },
                    {
                        'IndexName': "post_index",
                        'KeySchema': [
                            {
                                'AttributeName': 'draft',
                                'KeyType': 'HASH',
                            },
                            {
                                'AttributeName': 'post_date',
                                'KeyType': 'RANGE',
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 2,
                            'WriteCapacityUnits': 2
                        }
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'post_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'user_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'post_date',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'draft',
                        'AttributeType': 'N'
                    },
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
        self._blog_posts_table = self._db.Table(bp_table_name)

    def _create_tag_posts_table(self, table_names):
        tp_table_name = self._table_name("tag_posts")
        if tp_table_name not in table_names:
            self._client.create_table(
                TableName=tp_table_name,
                KeySchema=[{
                    'AttributeName': 'tag_id',
                    'KeyType': 'HASH'
                }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': "tag_index",
                        'KeySchema': [
                            {
                                'AttributeName': 'tag',
                                'KeyType': 'HASH',
                            },
                            {
                                'AttributeName': 'post_date',
                                'KeyType': 'RANGE',
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 2,
                            'WriteCapacityUnits': 2
                        }
                    },
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'tag_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'tag',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'post_date',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
        self._tag_posts_table = self._db.Table(tp_table_name)

    def _insert_tags(self, tags, post_id, post_date, draft):
        for t in tags:
            tag_id = "%s_%s" % (t, post_id)
            _ = self._tag_posts_table.put_item(
                Item={'tag_id': tag_id, 'tag': t, 'post_date': post_date,
                      'post_id': post_id, 'draft': draft}
            )

    def _delete_tags(self, tags, post_id):
        for t in tags:
            tag_id = "%s_%s" % (t, post_id)
            _ = self._tag_posts_table.delete_item(
                Key={'tag_id': tag_id}
            )
