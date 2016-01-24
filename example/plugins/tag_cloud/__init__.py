from flask_blogging import signals
from flask_blogging.sqlastorage import SQLAStorage
import sqlalchemy as sqla
from sqlalchemy import func


def get_tag_data(sqla_storage):
    engine = sqla_storage.engine
    with engine.begin() as conn:
        tag_posts_table = sqla_storage.tag_posts_table
        tag_table = sqla_storage.tag_table

        tag_cloud_stmt = sqla.select([
            tag_table.c.text,func.count(tag_posts_table.c.tag_id)]).group_by(
            tag_posts_table.c.tag_id
        ).where(tag_table.c.id == tag_posts_table.c.tag_id).limit(10)
        tag_cloud = conn.execute(tag_cloud_stmt).fetchall()
    return tag_cloud


def get_tag_cloud(app, engine, posts, meta, count, page):
    if isinstance(engine.storage, SQLAStorage):
        tag_cloud = get_tag_data(engine.storage)
        meta["tag_cloud"] = tag_cloud
    else:
        raise RuntimeError("Plugin only supports SQLAStorage. Given storage"
                           "not supported")
    return


def register(app):
    signals.index_posts_fetched.connect(get_tag_cloud)
    return
