from sqlalchemy import MetaData, Table, Column, BigInteger, String, Boolean, Integer, Text, TIMESTAMP
from sqlalchemy.sql import text


meta = MetaData()

ratings = Table(
    'ratings', meta,
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('rated_id', BigInteger, nullable=False),
    Column('rated_type', String(20), nullable=False),
    Column('rated_by', BigInteger, nullable=False),
    Column('rating_value', Integer),
    Column('title', String(255)),
    Column('review', Text),
    Column('rating_type', String(255)),
    Column('is_anonymous', Boolean),
    Column('created_at', TIMESTAMP),
    Column('updated_at', TIMESTAMP),
)

followers = Table(
    'followers', meta,
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('follower_id', BigInteger, nullable=False),
    Column('following_id', BigInteger, nullable=False),
    Column('followee_type', String(20), nullable=False),
    Column('status', String(255)),
    Column('followed_at', TIMESTAMP),
)

user_property = Table(
    'user_property', meta,
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('user_id', BigInteger, nullable=False),
    Column('property_id', BigInteger, nullable=False),
    Column('role', String(255)),
    Column('is_primary', Boolean),
    Column('added_at', TIMESTAMP),
)


