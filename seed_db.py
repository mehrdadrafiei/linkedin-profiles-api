from pymongo import MongoClient
from datetime import datetime
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv
import os
import ast

load_dotenv() 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGODB_DATABASE = os.getenv('MONGODB_DATABASE')


class DataMigration:
    def __init__(self, source_uri: str, target_uri: str):
        """
        Initialize connection to both source and target MongoDB instances
        """
        self.source_client = MongoClient(source_uri)
        self.target_client = MongoClient(target_uri)

        # Source collections
        self.source_db = self.source_client[MONGODB_DATABASE]
        self.profiles_complete = self.source_db['profiles_complete']

        # Target collections
        self.target_db = self.target_client[MONGODB_DATABASE]
        self.profiles = self.target_db['profiles']
        self.experiences = self.target_db['experiences']
        self.educations = self.target_db['educations']

    def format_duration(self, starts_at: Dict, ends_at: Optional[Dict]) -> str:
        """Format the duration string from start and end dates"""
        start_date = datetime(starts_at['year'], starts_at['month'],
                              starts_at['day']) if starts_at else None
        if not start_date:
            return None
        if ends_at:
            end_date = datetime(ends_at['year'], ends_at['month'], ends_at['day'])
            months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
            end_str = f"{end_date.strftime('%b %Y')}"
        else:
            end_str = "Present"
            months = (datetime.now().year - start_date.year) * \
                12 + datetime.now().month - start_date.month

        return f"{start_date.strftime('%b %Y')} - {end_str} · {months} mos."

    def format_date(self, date_dict: Dict) -> str:
        """Format date dictionary to string"""
        if not date_dict:
            return None
        return datetime(date_dict['year'], date_dict['month'], date_dict['day']).strftime('%b %Y')

    def transform_profile(self, source_doc: Dict) -> Dict:
        """Transform source profile document to target format"""
        return {
            "_id": source_doc["_id"],
            "name": source_doc["full_name"] if source_doc.get("full_name") else None,
            "position": source_doc["job_title"] if source_doc.get("job_title") else None,
            "location": f"{source_doc['location_country']}, {source_doc['location_name']}" 
            if source_doc.get("location_country") and source_doc.get("location_name") else None
            if source_doc.get('location_name') and source_doc.get('location_country') else None,
            "open_to_work": False,
            "about": source_doc["summary"] if source_doc.get("summary") else None,
            "url": f"https://www.linkedin.com/in/{source_doc['linkedin_username']}/"
        }

    def transform_experiences(self, profile_id: str, experiences: List[Dict]) -> List[Dict]:
        """Transform source experiences to target format"""
        experiences = ast.literal_eval(experiences)
        transformed = []
        for exp in experiences:
            transformed.append({
                "profile": profile_id,
                "company_page": f'https://{exp["company"]["linkedin_url"]}' if exp.get("company") else None,
                "role": exp["title"]["role"] if exp.get("title") else None,
                "work_at": exp["company"]["name"] if exp.get("company") else None,
                "duration": exp["start_date"],
                "location": exp["company"]["location"]["name"] if exp["company"] and exp["company"].get("location") else None,
                "role_summery": exp["summery"] if exp.get("summery") else None
            })
        return transformed

    def transform_educations(self, profile_id: str, educations: List[Dict]) -> List[Dict]:
        """Transform source educations to target format"""
        transformed = []
        educations = ast.literal_eval(educations)
        for edu in educations:
            transformed.append({
                "profile": profile_id,
                "university_url": edu["school"]["linkedin_url"] if edu.get("school") else None,
                "university_name": edu["school"]["name"] if edu.get("school") else None,
                "degree": edu["degrees"][0] if edu.get("degrees") else None,
                "field_of_study": ", ".join(edu["majors"]) if edu.get("majors") else None,
                "start_date": edu["start_date"] if edu.get("start_date") else None,
                "end_date": edu["end_date"] if edu.get("end_date") else None,
                "grade": None,  # Not available in source data
                "skills": None  # Not available in source data
            })
        return transformed

    def migrate(self):
        """Execute the migration process"""
        try:
            # Get all documents from source collection
            source_docs = self.profiles_complete.find()

            for doc in source_docs:
                # Transform and insert profile
                profile = self.transform_profile(doc)
                self.profiles.insert_one(profile)
                logger.info(f"Inserted profile for {profile['name']}")

                # Transform and insert experiences
                if doc.get("experience"):
                    experiences = self.transform_experiences(profile["_id"], doc["experience"])
                    if experiences:
                        self.experiences.insert_many(experiences)
                        logger.info(f"Inserted {len(experiences)
                                                } experiences for {profile['name']}")

                # Transform and insert educations
                if doc.get("education"):
                    educations = self.transform_educations(profile["_id"], doc["education"])
                    if educations:
                        self.educations.insert_many(educations)
                        logger.info(f"Inserted {len(educations)} educations for {profile['name']}")

            logger.info("Migration completed successfully")

        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")
            raise

    def cleanup(self):
        """Close MongoDB connections"""
        self.source_client.close()
        self.target_client.close()


if __name__ == "__main__":
    # Configure your MongoDB connection strings
    SOURCE_URI = os.getenv('MONGODB_URI')
    TARGET_URI = os.getenv('MONGODB_URI')

    # Initialize and run migration
    migration = DataMigration(SOURCE_URI, TARGET_URI)
    try:
        migration.migrate()
    finally:
        migration.cleanup()
