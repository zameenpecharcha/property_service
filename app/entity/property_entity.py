from sqlalchemy import MetaData, Table, Column, Integer, String, Float, TIMESTAMP, Boolean, Enum as SQLEnum, UUID
from sqlalchemy.sql import func
from ..models.property import PropertyType, PropertyStatus

meta = MetaData()

# Define the enum values explicitly
PROPERTY_TYPES = ['APARTMENT', 'VILLA', 'HOUSE', 'LAND']
PROPERTY_STATUSES = ['ACTIVE', 'INACTIVE', 'SOLD', 'RENTED']

properties = Table('properties', meta,
    Column('property_id', UUID, primary_key=True),
    Column('user_id', UUID, nullable=False),
    Column('title', String(100), nullable=False),
    Column('description', String(1000), nullable=False),
    Column('price', Float, nullable=False),
    Column('location', String(255), nullable=False),
    Column('property_type', SQLEnum(*PROPERTY_TYPES, name='propertytype', create_constraint=True), nullable=False),
    Column('status', SQLEnum(*PROPERTY_STATUSES, name='propertystatus', create_constraint=True), default='ACTIVE'),
    Column('images', String, nullable=True),  # JSON string of base64 images
    Column('bedrooms', Integer, nullable=True),
    Column('bathrooms', Integer, nullable=True),
    Column('area', Float, nullable=True),
    Column('year_built', Integer, nullable=True),
    Column('amenities', String, nullable=True),  # JSON string of amenities
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.now()),
    Column('updated_at', TIMESTAMP(timezone=True), onupdate=func.now()),
    Column('is_featured', Boolean, default=False),
    Column('views', Integer, default=0),
    Column('latitude', Float, nullable=True),
    Column('longitude', Float, nullable=True),
    Column('address', String(255), nullable=True),
    Column('city', String(100), nullable=False),
    Column('state', String(100), nullable=False),
    Column('country', String(100), nullable=False),
    Column('zip_code', String(20), nullable=True),
    Column('is_active', Boolean, default=True)
) 