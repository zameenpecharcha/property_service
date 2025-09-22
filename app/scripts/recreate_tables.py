from ..entity.property_entity import meta
from ..utils.db_connection import get_db_engine

def recreate_tables():
    engine = get_db_engine()
    
    # Drop all tables
    meta.drop_all(engine)
    
    # Create all tables
    meta.create_all(engine)
    
    print("Tables recreated successfully!")

if __name__ == "__main__":
    recreate_tables() 