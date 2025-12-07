"""
New RateMyProf scraper using GraphQL API.
Replaces the old REST API which is now deprecated.
"""

import requests
import json
import base64
import logging

logger = logging.getLogger(__name__)


class RateMyProfGraphQL:
    """Scrape professors from RateMyProf using the new GraphQL API."""
    
    BASE_URL = "https://www.ratemyprofessors.com/graphql"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Content-Type": "application/json"
    }
    
    def __init__(self, school_id: int = 1581):
        """
        Initialize with school ID.
        
        Args:
            school_id: The RateMyProf school ID (e.g., 1581 for Foothill College)
        """
        self.school_id = school_id
        self.school_id_encoded = self._encode_school_id(school_id)
    
    @staticmethod
    def _encode_school_id(school_id: int) -> str:
        """Encode school ID to base64 format required by GraphQL."""
        school_str = f"School-{school_id}"
        return base64.b64encode(school_str.encode()).decode()
    
    def fetch_professors(self, limit: int = None, offset: int = 0):
        """
        Fetch professors for the school.
        
        Args:
            limit: Maximum number of professors to fetch (None = fetch all)
            offset: For pagination (default 0)
        
        Returns:
            List of professor dicts with keys: id, firstName, lastName, avgRating, numRatings, department
        """
        professors = []
        cursor = None
        page = 0
        total_fetched = 0
        
        while True:
            page += 1
            logger.info(f"Fetching page {page} of professors...")
            
            try:
                results = self._fetch_page(cursor=cursor, first=100)
                
                if not results:
                    logger.info("No more professors to fetch")
                    break
                
                professors.extend(results["professors"])
                total_fetched += len(results["professors"])
                
                logger.info(f"  Fetched {len(results['professors'])} professors (total: {total_fetched})")
                
                # Check if we've hit the limit
                if limit and total_fetched >= limit:
                    professors = professors[:limit]
                    logger.info(f"Reached limit of {limit} professors")
                    break
                
                # Check if there are more pages
                if not results.get("has_next_page"):
                    logger.info("No more pages available")
                    break
                
                cursor = results.get("end_cursor")
            
            except Exception as e:
                logger.error(f"Error fetching page {page}: {str(e)}")
                raise
        
        return professors
    
    def _fetch_page(self, cursor: str = None, first: int = 100):
        """
        Fetch a single page of professors.
        
        Args:
            cursor: Pagination cursor (None for first page)
            first: Number of professors per page (max 100)
        
        Returns:
            Dict with keys: professors, has_next_page, end_cursor
        """
        query_variables = {
            "query": {
                "schoolID": self.school_id_encoded
            },
            "first": first
        }
        
        if cursor:
            query_variables["after"] = cursor
        
        query = """
        query newSearch($query: TeacherSearchQuery, $first: Int, $after: String) {
            newSearch {
                teachers(query: $query, first: $first, after: $after) {
                    edges {
                        node {
                            id
                            firstName
                            lastName
                            avgRating
                            numRatings
                            department
                        }
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
        """
        
        payload = {
            "query": query,
            "variables": query_variables
        }
        
        try:
            response = requests.post(
                self.BASE_URL,
                json=payload,
                headers=self.HEADERS,
                timeout=10
            )
            
            if response.status_code != 200:
                raise Exception(f"GraphQL API returned {response.status_code}: {response.text[:500]}")
            
            result = response.json()
            
            # Check for GraphQL errors
            if result.get("errors"):
                error_msg = result["errors"][0].get("message", "Unknown error")
                raise Exception(f"GraphQL error: {error_msg}")
            
            # Extract data
            teachers_data = result["data"]["newSearch"]["teachers"]
            
            professors = []
            for edge in teachers_data["edges"]:
                node = edge["node"]
                professors.append({
                    "id": node["id"],
                    "firstName": node["firstName"],
                    "lastName": node["lastName"],
                    "avgRating": node.get("avgRating"),
                    "numRatings": node.get("numRatings"),
                    "department": node.get("department", "Unknown")
                })
            
            page_info = teachers_data["pageInfo"]
            
            return {
                "professors": professors,
                "has_next_page": page_info["hasNextPage"],
                "end_cursor": page_info.get("endCursor")
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Response parsing error: {str(e)}")
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test: Fetch professors from Foothill College (school ID 1581)
    scraper = RateMyProfGraphQL(school_id=1581)
    profs = scraper.fetch_professors(limit=10)
    
    print(f"\nFetched {len(profs)} professors:")
    for prof in profs:
        print(f"  {prof['firstName']} {prof['lastName']} - {prof['department']} - Avg: {prof['avgRating']}")
