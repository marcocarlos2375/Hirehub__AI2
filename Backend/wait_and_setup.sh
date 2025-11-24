#!/bin/bash

echo "======================================================================="
echo "Waiting for Docker Container to be Ready"
echo "======================================================================="

# Wait for container to be running
MAX_ATTEMPTS=60
attempt=0

while [ $attempt -lt $MAX_ATTEMPTS ]; do
    if docker-compose ps api | grep -q "Up"; then
        echo "✅ Docker container is up!"
        break
    fi

    attempt=$((attempt + 1))
    echo "Waiting for container... ($attempt/$MAX_ATTEMPTS)"
    sleep 5
done

if [ $attempt -eq $MAX_ATTEMPTS ]; then
    echo "❌ Container failed to start after $((MAX_ATTEMPTS * 5)) seconds"
    exit 1
fi

# Wait an additional 10 seconds for services to fully initialize
echo "Waiting for services to initialize..."
sleep 10

echo ""
echo "======================================================================="
echo "Step 1: Running Database Migration"
echo "======================================================================="

docker-compose exec -T api psql $DATABASE_URL < migrations/001_learning_resources.sql

if [ $? -eq 0 ]; then
    echo "✅ Database migration completed successfully!"
else
    echo "❌ Database migration failed"
    exit 1
fi

echo ""
echo "======================================================================="
echo "Step 2: Seeding Learning Resources"
echo "======================================================================="

docker-compose exec -T api python3 scripts/seed_resources.py --clear

if [ $? -eq 0 ]; then
    echo "✅ Seeding completed successfully!"
else
    echo "❌ Seeding failed"
    exit 1
fi

echo ""
echo "======================================================================="
echo "Setup Complete!"
echo "======================================================================="
echo ""
echo "Next steps:"
echo "1. Test API endpoints with curl (see IMPLEMENTATION_SUMMARY.md)"
echo "2. Verify adaptive question workflow"
echo ""
