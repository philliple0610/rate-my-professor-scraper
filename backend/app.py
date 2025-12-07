from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql
import logging

pymysql.install_as_MySQLdb()
app = Flask(__name__)
CORS(app)

# test

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://prof_user:123mySQL@localhost/rate_professor'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ratemyprof_id = db.Column(db.String(255), unique=True, nullable=True)  # GraphQL ID (base64 encoded)
    name = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(255), nullable=False)
    class_name = db.Column(db.String(255), nullable=False)
    avg_grade = db.Column(db.String(10))
    overall_rating = db.Column(db.Float, nullable=True)  # RateMyProf overall rating
    num_ratings = db.Column(db.Integer, nullable=True)  # Number of ratings on RateMyProf

@app.route("/")
def index():
    return "Professor Ratings API is running."

# GET all professors
@app.route("/api/professors", methods=["GET"])
def get_professors():
    profs = Professor.query.all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "department": p.department,
            "class": p.class_name,
            "avgGrade": p.avg_grade
        }
        for p in profs
    ])

# GET single professor by ID
@app.route("/api/professors/<int:prof_id>", methods=["GET"])
def get_professor(prof_id):
    p = Professor.query.get_or_404(prof_id)
    return jsonify({
        "id": p.id,
        "name": p.name,
        "department": p.department,
        "class": p.class_name,
        "avgGrade": p.avg_grade,
        "ratemyprofId": p.ratemyprof_id,
        "overallRating": p.overall_rating,
        "numRatings": p.num_ratings
    })

# POST endpoint to trigger scraping
@app.route("/api/scrape-professors", methods=["POST"])
def scrape_professors():
    """
    Trigger scraping of professors from RateMyProf.
    
    Request body:
    {
        "school_id": 1581,    # optional, defaults to 1581
        "limit": null         # optional, max professors to fetch (null = all)
    }
    """
    try:
        from scraper_service import scrape_and_store_professors
        
        data = request.get_json() or {}
        school_id = data.get("school_id", 1581)
        limit = data.get("limit", None)
        
        logger.info(f"Scrape requested for school_id={school_id}, limit={limit}")
        
        result = scrape_and_store_professors(school_id=school_id, limit=limit)
        
        return jsonify(result), 200 if result["success"] else 400
    
    except Exception as e:
        logger.error(f"Scrape endpoint error: {str(e)}")
        return jsonify({
            "success": False,
            "count": 0,
            "message": f"Internal server error: {str(e)}"
        }), 500

# GET scraping status / info
@app.route("/api/professors/stats", methods=["GET"])
def professor_stats():
    """Get general stats about professors in the database."""
    total = Professor.query.count()
    with_rmp_id = Professor.query.filter(Professor.ratemyprof_id.isnot(None)).count()
    with_rating = Professor.query.filter(Professor.overall_rating.isnot(None)).count()
    
    return jsonify({
        "total": total,
        "withRatings": with_rating,
        "fromRateMyProf": with_rmp_id
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)
