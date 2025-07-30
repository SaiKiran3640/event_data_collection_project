from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    date_string = Column(String(500), nullable=True)  # Keep the full date string
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    organizer = Column(String(255), nullable=True)
    price = Column(String(100), nullable=True)
    source_url = Column(String(1000), nullable=False, unique=True)  # Use as unique identifier
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Laravel-friendly timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Event(title='{self.title}', location='{self.location}', url='{self.source_url}')>"

