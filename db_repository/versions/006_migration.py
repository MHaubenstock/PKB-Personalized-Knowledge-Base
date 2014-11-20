from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user_topic = Table('user_topic', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', String(length=40)),
    Column('description', String(length=1000)),
    Column('parent', String(length=40)),
    Column('user_id', Integer),
    Column('tags', PickleType),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user_topic'].columns['tags'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user_topic'].columns['tags'].drop()
