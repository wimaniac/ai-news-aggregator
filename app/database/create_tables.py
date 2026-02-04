from models import Base
from connection import engine

if __name__ == "__main__":
    print("Creating all tables...")
    Base.metadata.create_all(engine)
    print("✅ Tables created successfully.")

