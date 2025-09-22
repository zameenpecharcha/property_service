from ..entity.property_entity import properties, meta
from .db_connection import get_db_engine

def init_db():
    engine = get_db_engine()
    # Drop all tables first
    meta.drop_all(engine)
    # Create all tables
    meta.create_all(engine)
    print("Database tables recreated successfully!")

if __name__ == "__main__":
    init_db() 