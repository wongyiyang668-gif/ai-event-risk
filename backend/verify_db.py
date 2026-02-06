from app.db.models import Base
from app.db.session import engine

def verify_tables():
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    verify_tables()
