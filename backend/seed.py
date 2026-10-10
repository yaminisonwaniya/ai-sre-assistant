"""Database seed script populating 15 sample requirements into a default project."""
import json
import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import Base, engine, SessionLocal
from app.models.project import Project
from app.models.requirement import Requirement


def seed_database():
    """Populate database with default project and 15 sample requirements."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check or create default project
        project = db.query(Project).filter(Project.name == "Healthcare Patient Portal SRS").first()
        if not project:
            project = Project(
                name="Healthcare Patient Portal SRS",
                description="Software Requirements Specification for a HIPAA-compliant online patient healthcare management portal."
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            print(f"Created Project: {project.name} (ID: {project.id})")
        else:
            print(f"Using existing Project: {project.name} (ID: {project.id})")

        # Locate sample requirements JSON file
        json_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_requirements.json")
        if not os.path.exists(json_path):
            json_path = os.path.join(os.path.dirname(__file__), "sample_requirements.json")

        if not os.path.exists(json_path):
            print(f"Error: Sample data file not found at {json_path}")
            return

        with open(json_path, "r", encoding="utf-8") as f:
            requirements_data = json.load(f)

        seeded_count = 0
        for item in requirements_data:
            existing = db.query(Requirement).filter(
                Requirement.project_id == project.id,
                Requirement.req_code == item["req_code"]
            ).first()

            if not existing:
                req = Requirement(
                    project_id=project.id,
                    req_code=item["req_code"],
                    text=item["text"],
                    type=item.get("type", "UNCLASSIFIED"),
                    subtype=item.get("subtype", "GENERAL"),
                    quality_score=item.get("quality_score", 100.0),
                    status=item.get("status", "DRAFT")
                )
                db.add(req)
                seeded_count += 1

        db.commit()
        total_reqs = db.query(Requirement).filter(Requirement.project_id == project.id).count()
        print(f"Successfully seeded {seeded_count} new requirements. Total requirements in project: {total_reqs}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
