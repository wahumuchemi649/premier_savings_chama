
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = "postgresql://postgres:42131607k@db.uprkkmzyokknsrbezczq.supabase.co:5432/postgres"

# The engine acts as the core interface to the database
engine = create_engine(DATABASE_URL, echo=False)

# SessionLocal is a class factory for database session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The base class that maps our Python classes directly to database tables
Base = declarative_base()
