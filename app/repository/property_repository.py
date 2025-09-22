from ..entity.property_entity import properties
from sqlalchemy.orm import sessionmaker
from ..utils.db_connection import get_db_engine
import json
from ..models.property import PropertyType, PropertyStatus
import uuid

SessionLocal = sessionmaker(bind=get_db_engine())

# Map proto enum int to database enum string for property type
proto_to_db_property_type = {
    0: 'APARTMENT',
    1: 'VILLA',
    2: 'HOUSE',
    3: 'LAND'
}

# Map proto enum int to database enum string for status
proto_to_db_property_status = {
    0: 'ACTIVE',
    1: 'INACTIVE',
    2: 'SOLD',
    3: 'RENTED'
}

def get_property_by_id(property_id):
    session = SessionLocal()
    try:
        # Convert string to UUID
        property_uuid = uuid.UUID(property_id)
        query = properties.select().where(properties.c.property_id == property_uuid)
        property = session.execute(query).fetchone()
        return property
    except ValueError:
        return None
    finally:
        session.close()

def create_property(property_data):
    session = SessionLocal()
    try:
        # Convert RepeatedScalarContainer to list before JSON serialization
        property_data['images'] = json.dumps(list(property_data.get('images', [])))
        property_data['amenities'] = json.dumps(list(property_data.get('amenities', [])))
        
        # Map proto enum int to database enum string
        property_data['property_type'] = proto_to_db_property_type.get(property_data['property_type'], 'APARTMENT')
        property_data['status'] = proto_to_db_property_status.get(property_data['status'], 'ACTIVE')
        
        # Convert string UUIDs to UUID objects
        property_data['property_id'] = uuid.UUID(property_data['property_id'])
        property_data['user_id'] = uuid.UUID(property_data['user_id'])
        
        result = session.execute(
            properties.insert().returning(properties.c.property_id).values(**property_data)
        )
        property_id = result.fetchone()[0]
        session.commit()
        return str(property_id)  # Convert UUID back to string
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_property(property_id, property_data):
    session = SessionLocal()
    try:
        # Convert lists to JSON strings
        if 'images' in property_data:
            property_data['images'] = json.dumps(list(property_data['images']))
        if 'amenities' in property_data:
            property_data['amenities'] = json.dumps(list(property_data['amenities']))
        
        # Map proto enum int to database enum string
        if 'property_type' in property_data:
            property_data['property_type'] = proto_to_db_property_type.get(property_data['property_type'], 'APARTMENT')
        if 'status' in property_data:
            property_data['status'] = proto_to_db_property_status.get(property_data['status'], 'ACTIVE')
        
        # Convert string UUIDs to UUID objects
        if 'user_id' in property_data:
            property_data['user_id'] = uuid.UUID(property_data['user_id'])
        
        # Convert property_id to UUID
        property_uuid = uuid.UUID(property_id)
        
        result = session.execute(
            properties.update()
            .where(properties.c.property_id == property_uuid)
            .values(**property_data)
        )
        session.commit()
        return result.rowcount > 0
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_property(property_id):
    session = SessionLocal()
    try:
        # Convert string to UUID
        property_uuid = uuid.UUID(property_id)
        
        result = session.execute(
            properties.delete().where(properties.c.property_id == property_uuid)
        )
        session.commit()
        return result.rowcount > 0
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_user_properties(user_id):
    session = SessionLocal()
    query = properties.select().where(properties.c.user_id == user_id)
    user_properties = session.execute(query).fetchall()
    session.close()
    return user_properties

def search_properties(query=None, property_type=None, min_price=None, max_price=None, 
                  location=None, min_bedrooms=None, min_bathrooms=None, 
                  min_area=None, max_area=None, skip=0, limit=10):
    session = SessionLocal()
    try:
        # Start with base query
        search_query = properties.select()

        # Add filters based on parameters
        if query:
            search_pattern = f"%{query}%"
            search_query = search_query.where(
                (properties.c.title.ilike(search_pattern)) |
                (properties.c.description.ilike(search_pattern)) |
                (properties.c.location.ilike(search_pattern)) |
                (properties.c.city.ilike(search_pattern))
            )

        if property_type is not None:
            search_query = search_query.where(properties.c.property_type == property_type)
        
        if min_price is not None:
            search_query = search_query.where(properties.c.price >= min_price)
        
        if max_price is not None:
            search_query = search_query.where(properties.c.price <= max_price)
        
        if location:
            location_pattern = f"%{location}%"
            search_query = search_query.where(properties.c.location.ilike(location_pattern))
        
        if min_bedrooms is not None:
            search_query = search_query.where(properties.c.bedrooms >= min_bedrooms)
        
        if min_bathrooms is not None:
            search_query = search_query.where(properties.c.bathrooms >= min_bathrooms)
        
        if min_area is not None:
            search_query = search_query.where(properties.c.area >= min_area)
        
        if max_area is not None:
            search_query = search_query.where(properties.c.area <= max_area)

        # Add pagination
        search_query = search_query.offset(skip).limit(limit)

        # Execute query
        results = session.execute(search_query).fetchall()
        return results
    except Exception as e:
        raise e
    finally:
        session.close()

def get_properties(skip=0, limit=10, property_type=None, status=None, 
                  min_price=None, max_price=None, city=None):
    session = SessionLocal()
    try:
        # Start with base query
        query = properties.select()
        
        # Add filters if provided
        if property_type:
            query = query.where(properties.c.property_type == property_type)
        if status:
            query = query.where(properties.c.status == status)
        if min_price is not None:
            query = query.where(properties.c.price >= min_price)
        if max_price is not None:
            query = query.where(properties.c.price <= max_price)
        if city:
            query = query.where(properties.c.city == city)
            
        # Add pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        results = session.execute(query).fetchall()
        return results
    except Exception as e:
        raise e
    finally:
        session.close()

def increment_view_count(property_id):
    session = SessionLocal()
    try:
        # Convert string to UUID
        property_uuid = uuid.UUID(property_id)
        
        # Get current views and increment
        query = properties.select().where(properties.c.property_id == property_uuid)
        property = session.execute(query).fetchone()
        
        if not property:
            return False
            
        current_views = property.views or 0
        new_views = current_views + 1
        
        # Update views
        result = session.execute(
            properties.update()
            .where(properties.c.property_id == property_uuid)
            .values(views=new_views)
        )
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close() 