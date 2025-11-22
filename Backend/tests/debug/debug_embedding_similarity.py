"""
Debug script to see actual embedding similarity scores.
This will tell us if the threshold (0.55) is too high or if the model genuinely sees them as different.
"""

import sys
sys.path.insert(0, '/app')

from core.embeddings import get_embedding, calculate_cosine_similarity

print("=" * 80)
print("EMBEDDING SIMILARITY DEBUG")
print("=" * 80)

# Test pairs that are failing
test_pairs = [
    # Industry matching
    ("SaaS", "Technology"),
    ("SaaS", "Software"),
    ("Technology", "Software"),

    # Domain matching
    ("Scalable cloud infrastructure", "Built scalable microservices handling 1M+ requests per day"),
    ("Scalable cloud infrastructure", "scalable systems"),
    ("Scalable cloud infrastructure", "cloud migration project"),

    ("Microservices architecture patterns", "Built scalable microservices handling 1M+ requests per day"),
    ("Microservices architecture patterns", "microservices architecture"),

    ("API design best practices", "Designed and developed REST APIs used by 50+ internal services"),
    ("API design best practices", "REST APIs"),

    # Hard skills matching
    ("RESTful API design", "REST APIs"),
    ("RESTful API design", "Developed REST APIs using Python Flask"),

    ("AWS (EC2, Lambda, RDS, S3)", "AWS"),
    ("AWS (EC2, Lambda, RDS, S3)", "Led team in cloud migration project to AWS"),

    ("Docker", "Docker"),
    ("Kubernetes", "Kubernetes"),
    ("Python", "Python"),
]

print("\nCalculating similarities (using Google text-embedding-004)...\n")

for phrase1, phrase2 in test_pairs:
    # Get embeddings
    emb1 = get_embedding(phrase1)
    emb2 = get_embedding(phrase2)

    # Calculate similarity
    similarity = calculate_cosine_similarity(emb1, emb2)

    # Determine if it passes threshold
    threshold = 0.55
    passes = "✅ MATCH" if similarity >= threshold else "❌ NO MATCH"

    print(f"{passes} | {similarity:.3f} | '{phrase1}' vs '{phrase2}'")

print("\n" + "=" * 80)
print("Threshold: 0.55 (55%)")
print("=" * 80)
print("\nInterpretation:")
print("- Scores >= 0.55: Will be counted as matches")
print("- Scores < 0.55: Will NOT be counted as matches")
print("\nIf many related pairs score < 0.55, we should lower the threshold!")
print("=" * 80)
