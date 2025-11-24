#!/usr/bin/env python3
"""
Seed learning resources database and vector store.

This script:
1. Reads learning resources from seed_data/learning_resources.json
2. Populates PostgreSQL database using SQLAlchemy models
3. Creates embeddings for each resource
4. Populates Qdrant vector store for semantic search

Usage:
    python scripts/seed_resources.py [--clear]

    --clear: Clear existing data before seeding
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import uuid
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from langchain_core.documents import Document

from models.learning_resources import LearningResource, Base
from core.langchain_config import get_embeddings, get_learning_resources_vectorstore


def load_seed_data(json_file: str = "seed_data/learning_resources.json") -> List[Dict[str, Any]]:
    """Load learning resources from JSON file."""
    json_path = project_root / json_file

    if not json_path.exists():
        raise FileNotFoundError(f"Seed data file not found: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✅ Loaded {len(data)} resources from {json_file}")
    return data


def clear_database(session):
    """Clear existing learning resources from database."""
    try:
        count = session.query(LearningResource).count()
        if count > 0:
            session.query(LearningResource).delete()
            session.commit()
            print(f"🗑️  Cleared {count} existing resources from database")
        else:
            print("ℹ️  Database is already empty")
    except Exception as e:
        session.rollback()
        print(f"⚠️  Error clearing database: {str(e)}")


def clear_vector_store():
    """Clear existing learning resources from Qdrant."""
    try:
        from qdrant_client import QdrantClient

        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

        # Check if collection exists
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if "learning_resources" in collection_names:
            # Delete collection
            client.delete_collection("learning_resources")
            print("🗑️  Cleared existing learning_resources collection from Qdrant")
        else:
            print("ℹ️  Qdrant collection doesn't exist yet")

    except Exception as e:
        print(f"⚠️  Error clearing vector store: {str(e)}")


def seed_database(session, resources: List[Dict[str, Any]]) -> List[LearningResource]:
    """Populate PostgreSQL database with learning resources."""
    print("\n📦 Seeding PostgreSQL database...")

    db_resources = []

    for i, resource_data in enumerate(resources, 1):
        try:
            # Create UUID from string ID (deterministic)
            resource_id = uuid.uuid5(uuid.NAMESPACE_DNS, resource_data["id"])

            # Create LearningResource model
            resource = LearningResource(
                id=resource_id,
                title=resource_data["title"],
                description=resource_data["description"],
                type=resource_data["type"],
                provider=resource_data["provider"],
                url=resource_data["url"],
                duration_days=resource_data["duration_days"],
                difficulty=resource_data["difficulty"],
                cost=resource_data["cost"],
                skills_covered=resource_data["skills_covered"],
                rating=resource_data.get("rating"),
                completion_certificate=resource_data.get("completion_certificate", False),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(resource)
            db_resources.append(resource)

            if i % 10 == 0:
                print(f"   Added {i}/{len(resources)} resources...")

        except Exception as e:
            print(f"❌ Error adding resource {resource_data['id']}: {str(e)}")
            continue

    # Commit all resources
    try:
        session.commit()
        print(f"✅ Successfully seeded {len(db_resources)} resources to PostgreSQL")
        return db_resources
    except Exception as e:
        session.rollback()
        print(f"❌ Error committing to database: {str(e)}")
        return []


def seed_vector_store(resources: List[Dict[str, Any]]) -> bool:
    """Populate Qdrant vector store with learning resources."""
    print("\n🔍 Seeding Qdrant vector store...")

    try:
        # Get vector store and embeddings
        vectorstore = get_learning_resources_vectorstore()

        # Prepare documents for embedding
        documents = []
        metadatas = []

        for resource_data in resources:
            # Create document with description as content
            doc_content = f"{resource_data['title']}: {resource_data['description']}"

            # Create metadata (all searchable fields)
            metadata = {
                "id": resource_data["id"],
                "title": resource_data["title"],
                "type": resource_data["type"],
                "provider": resource_data["provider"],
                "url": resource_data["url"],
                "duration_days": resource_data["duration_days"],
                "difficulty": resource_data["difficulty"],
                "cost": resource_data["cost"],
                "skills_covered": resource_data["skills_covered"],
                "rating": resource_data.get("rating", 0.0),
                "completion_certificate": resource_data.get("completion_certificate", False)
            }

            doc = Document(page_content=doc_content, metadata=metadata)
            documents.append(doc)

        print(f"   Embedding and indexing {len(documents)} documents...")

        # Add documents to vector store (creates embeddings automatically)
        # Process in batches of 10 to avoid rate limits
        batch_size = 10
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            vectorstore.add_documents(batch)
            print(f"   Indexed {min(i+batch_size, len(documents))}/{len(documents)} resources...")

        print(f"✅ Successfully seeded {len(documents)} resources to Qdrant")
        return True

    except Exception as e:
        print(f"❌ Error seeding vector store: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_seeding(session):
    """Verify that seeding was successful."""
    print("\n✅ Verification:")

    # Check database
    try:
        count = session.query(LearningResource).count()
        print(f"   PostgreSQL: {count} resources")

        # Sample query
        sample = session.query(LearningResource).filter(
            LearningResource.type == "course"
        ).limit(3).all()

        if sample:
            print(f"   Sample courses:")
            for resource in sample:
                print(f"      - {resource.title} ({resource.duration_days} days, {resource.difficulty})")
    except Exception as e:
        print(f"   ❌ Database verification failed: {str(e)}")

    # Check vector store
    try:
        vectorstore = get_learning_resources_vectorstore()

        # Test semantic search
        test_query = "Learn AWS Lambda serverless"
        results = vectorstore.similarity_search(test_query, k=3)

        print(f"\n   Qdrant: Vector store operational")
        print(f"   Sample search for '{test_query}':")
        for i, doc in enumerate(results, 1):
            print(f"      {i}. {doc.metadata.get('title')} ({doc.metadata.get('type')})")

    except Exception as e:
        print(f"   ❌ Vector store verification failed: {str(e)}")


def main():
    """Main seeding script."""
    import argparse

    parser = argparse.ArgumentParser(description="Seed learning resources database")
    parser.add_argument("--clear", action="store_true", help="Clear existing data before seeding")
    args = parser.parse_args()

    print("=" * 70)
    print("🌱 Learning Resources Seeding Script")
    print("=" * 70)

    # Load seed data
    try:
        resources = load_seed_data()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # Setup database connection
    db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/hirehub")
    print(f"\n📊 Connecting to database: {db_url.split('@')[1] if '@' in db_url else 'local'}")

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Create tables if they don't exist
    try:
        Base.metadata.create_all(engine)
        print("✅ Database tables ready")
    except Exception as e:
        print(f"⚠️  Error creating tables: {str(e)}")

    # Clear existing data if requested
    if args.clear:
        print("\n🗑️  Clearing existing data...")
        clear_database(session)
        clear_vector_store()

    # Seed database
    db_resources = seed_database(session, resources)

    if not db_resources:
        print("❌ Database seeding failed. Aborting.")
        session.close()
        sys.exit(1)

    # Seed vector store
    success = seed_vector_store(resources)

    if not success:
        print("⚠️  Vector store seeding failed, but database was populated")

    # Verify seeding
    verify_seeding(session)

    # Cleanup
    session.close()

    print("\n" + "=" * 70)
    if success:
        print("✅ Seeding completed successfully!")
    else:
        print("⚠️  Seeding completed with warnings")
    print("=" * 70)
    print("\nYou can now use the ResourceMatcher to find learning resources!")
    print("Example:")
    print("    from core.resource_matcher import find_resources_for_gap")
    print("    gap = {'title': 'AWS Lambda', 'description': '...'}")
    print("    results = find_resources_for_gap(gap, user_level='intermediate')")
    print()


if __name__ == "__main__":
    main()
