# database/db_config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use the new password you just set in MySQL Workbench
DB_URI = "mysql+pymysql://root:#Sql&630@localhost:3306/eventdb"
engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)