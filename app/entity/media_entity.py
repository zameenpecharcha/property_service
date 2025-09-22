from sqlalchemy import MetaData, Table, Column, BigInteger, String, Text, Integer, TIMESTAMP, text


meta = MetaData()

media = Table(
    'media',
    meta,
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('context_id', BigInteger),
    Column('context_type', String(255)),
    Column('media_type', String(255)),
    Column('media_url', Text),
    Column('media_order', Integer),
    Column('media_size', BigInteger),
    Column('caption', Text),
    Column('uploaded_at', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP')),
)


