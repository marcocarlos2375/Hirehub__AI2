collection_name = "resume_match_demo"

client.recreate_collection(
    collection_name=collection_name,
    vectors_config={"size": 384, "distance": "Cosine"}
)

# Exemple de contenu de CV
resume_sentences = [
    "Developed REST APIs using Flask and FastAPI",
    "Built responsive UIs with Vue.js and Nuxt.js",
    "Implemented CI/CD pipelines with Docker and GitHub Actions",
    "Deployed scalable services on AWS",
]

# Exemple de contenu d'une offre d'emploi
job_description = [
    "Looking for a backend developer experienced with Python and Flask.",
    "Experience with Docker and CI/CD pipelines is required.",
    "Frontend knowledge with Vue.js and React.js (important).",
    "Knowledge of cloud deployment using AWS or GCP is appreciated."
]

# Encodage
resume_vectors = model.encode(resume_sentences).tolist()
job_vectors = model.encode(job_description).tolist()

# Insertion dans Qdrant
points = [
    {"id": i, "vector": v, "payload": {"source": "resume", "text": t}}
    for i, (v, t) in enumerate(zip(resume_vectors, resume_sentences))
] + [
    {"id": 100 + i, "vector": v, "payload": {"source": "job", "text": t}}
    for i, (v, t) in enumerate(zip(job_vectors, job_description))
]

client.upsert(collection_name=collection_name, points=points)
print("✅ Données insérées dans Qdrant")