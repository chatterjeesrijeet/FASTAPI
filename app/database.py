

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base() # will be used to create the tables 



from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://<user_name>:<password>@<ip-address/hostname>/<database name>"

engine = create_engine(url = "postgresql://postgres:1234@localhost/fastapi")

SessionLocal = sessionmaker(autocommit = False, 
                            autoflush = False, 
                            bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
