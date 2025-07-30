from database.db_config import SessionLocal
from database.model import Base, Event
from scraper.site1_scraper import scrape_events
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
import logging

from database.db_config import engine

# Set up comprehensive logging  
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

def upsert_events_to_db(events):
    """Save/update events using source_url as unique identifier"""
    session = SessionLocal()
    
    inserted_count = 0
    updated_count = 0
    error_count = 0
    
    try:
        logger.info(f"💾 Processing {len(events)} events for database insertion...")
        
        for i, event_data in enumerate(events, 1):
            try:
                # Check if event already exists
                existing_event = session.query(Event).filter(
                    Event.source_url == event_data.get('source_url')
                ).first()
                
                if existing_event:
                    # Update existing event
                    existing_event.title = event_data.get('title', 'Unknown')
                    existing_event.date_string  = event_data.get('date_string', '')
                    existing_event.location = event_data.get('location', '')
                    existing_event.description = event_data.get('description', '')
                    existing_event.organizer = event_data.get('organizer', '')
                    existing_event.price = event_data.get('price', '')
                    # updated_at will be automatically set by SQLAlchemy
                    
                    updated_count += 1
                    logger.info(f"🔄 [{i}/{len(events)}] Updated: {existing_event.title[:50]}...")
                    
                else:
                    # Insert new event
                    event = Event(
                        title=event_data.get('title', 'Unknown'),
                        date_string =event_data.get('date_string', ''),
                        location=event_data.get('location', ''),
                        description=event_data.get('description', ''),
                        organizer=event_data.get('organizer', ''),
                        price=event_data.get('price', ''),
                        source_url=event_data.get('source_url', '')
                    )
                    
                    session.add(event)
                    inserted_count += 1
                    logger.info(f"✅ [{i}/{len(events)}] Inserted: {event.title[:50]}...")
                
                # Commit every 50 records to avoid large transactions
                if i % 50 == 0:
                    session.commit()
                    logger.info(f"🔄 Committed batch {i//50}: {inserted_count} new, {updated_count} updated")
                
            except Exception as e:
                session.rollback()
                error_count += 1
                logger.error(f"❌ Error processing event {i}: {e}")
                # Continue with next event
        
        # Final commit
        session.commit()
        
    except Exception as e:
        session.rollback()
        logger.error(f"💥 Fatal database error: {e}")
        raise
    finally:
        session.close()
    
    # Final summary
    logger.info(f"\n📊 DATABASE OPERATION SUMMARY:")
    logger.info(f"{'='*50}")
    logger.info(f"✅ New events inserted: {inserted_count}")
    logger.info(f"🔄 Existing events updated: {updated_count}")
    logger.info(f"❌ Errors encountered: {error_count}")
    logger.info(f"📈 Total processed: {len(events)}")
    logger.info(f"💾 Database operations complete!")

def main():
    """Main execution function"""
    logger.info("🚀 Starting Eventbrite scraping process...")
    
    try:
        # Step 1: Scrape events
        logger.info("📡 Phase 1: Web scraping...")
        events = scrape_events()
        
        if not events:
            logger.warning("⚠️ No events scraped. Exiting.")
            return
        
        logger.info(f"📥 Scraping complete: {len(events)} events collected")
        
        # Step 2: Save to database
        logger.info("💾 Phase 2: Database operations...")
        upsert_events_to_db(events)
        
        logger.info("🎉 Complete! Scraping and database operations finished successfully!")
        
    except Exception as e:
        logger.error(f"💥 Fatal error in main process: {e}")
        raise

if __name__ == "__main__":
    main()