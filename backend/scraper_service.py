"""
Scraper service module to integrate RateMyProf GraphQL API with Flask database.
Handles fetching, transforming, and upserting professor data.
"""

from ratemyprof_graphql import RateMyProfGraphQL
import logging

logger = logging.getLogger(__name__)


def scrape_and_store_professors(school_id: int = 1581, limit: int = None):
    """
    Scrape professors from RateMyProf GraphQL API and store/update them in the database.
    
    Args:
        school_id: RateMyProf school ID (default: 1074 for UC Irvine)
        limit: Maximum professors to fetch (None = fetch all)
    
    Returns:
        dict with keys: success (bool), count (int), message (str)
    """
    try:
        # Import here to avoid circular imports
        from app import app, db, Professor
        
        with app.app_context():
            logger.info(f"Starting scrape for school_id={school_id}")
            
            # Initialize GraphQL scraper
            scraper = RateMyProfGraphQL(school_id=school_id)
            professors_list = scraper.fetch_professors(limit=limit)
            
            if not professors_list:
                return {"success": False, "count": 0, "message": "No professors found"}
            
            count = 0
            errors = []
            
            # Iterate through scraped professors and upsert to database
            for prof_data in professors_list:
                try:
                    rmp_id = prof_data["id"]  # This is the GraphQL ID (base64 encoded)
                    
                    # Try to find existing professor by ratemyprof_id
                    existing = Professor.query.filter_by(ratemyprof_id=rmp_id).first()
                    
                    full_name = f"{prof_data['firstName']} {prof_data['lastName']}"
                    
                    if existing:
                        # Update existing professor
                        existing.name = full_name
                        existing.department = prof_data.get("department", "Unknown")
                        existing.overall_rating = prof_data.get("avgRating")
                        existing.num_ratings = prof_data.get("numRatings")
                        logger.debug(f"Updated professor: {full_name}")
                    else:
                        # Create new professor
                        new_prof = Professor(
                            ratemyprof_id=rmp_id,
                            name=full_name,
                            department=prof_data.get("department", "Unknown"),
                            class_name="",  # Will need to be filled manually or via another source
                            avg_grade=None,
                            overall_rating=prof_data.get("avgRating"),
                            num_ratings=prof_data.get("numRatings")
                        )
                        db.session.add(new_prof)
                        logger.debug(f"Added new professor: {full_name}")
                    
                    count += 1
                except Exception as e:
                    error_msg = f"Error processing professor: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Commit all changes
            db.session.commit()
            logger.info(f"Successfully processed {count} professors")
            
            message = f"Scraped and stored {count} professors"
            if errors:
                message += f" ({len(errors)} errors)"
            
            return {
                "success": True,
                "count": count,
                "message": message,
                "errors": errors if errors else None
            }
    
    except Exception as e:
        logger.error(f"Fatal error during scraping: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "count": 0,
            "message": f"Scraping failed: {str(e)}"
        }


def get_professor_by_ratemyprof_id(ratemyprof_id: str):
    """Retrieve a professor by their RateMyProf ID."""
    from app import app, Professor
    
    with app.app_context():
        return Professor.query.filter_by(ratemyprof_id=ratemyprof_id).first()


def update_professor_details(prof_id: int, **kwargs):
    """
    Update professor details (department, class_name, avg_grade).
    
    Args:
        prof_id: Database professor ID
        **kwargs: Fields to update (department, class_name, avg_grade)
    """
    from app import app, db, Professor
    
    with app.app_context():
        prof = Professor.query.get(prof_id)
        if not prof:
            return None
        
        allowed_fields = {"department", "class_name", "avg_grade"}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(prof, key, value)
        
        db.session.commit()
        return prof
