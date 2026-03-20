#!/bin/bash

set -e  # Exit on error

echo "======================================"
echo "🔧 FIXING AND REBUILDING SYSTEM"
echo "======================================"
echo ""

echo "Step 1: Stopping all containers..."
docker-compose down
echo "✅ Containers stopped"
echo ""

echo "Step 2: Removing old images to force rebuild..."
docker-compose down -v
docker image rm -f analysis-basket-api analysis-basket-worker analysis-basket-flower 2>/dev/null || true
echo "✅ Old images removed"
echo ""

echo "Step 3: Building fresh images (this will take a few minutes)..."
docker-compose build --no-cache --progress=plain
echo "✅ Images built"
echo ""

echo "Step 4: Starting services..."
docker-compose up -d
echo "✅ Services started"
echo ""

echo "Step 5: Waiting 15 seconds for services to initialize..."
for i in {15..1}; do
    echo -ne "  Waiting... $i seconds remaining\r"
    sleep 1
done
echo ""
echo "✅ Wait complete"
echo ""

echo "Step 6: Checking container status..."
docker-compose ps
echo ""

echo "Step 7: Testing API health endpoint..."
sleep 2
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health || echo "FAILED")

if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    echo "✅ ✅ ✅ SUCCESS! API is working!"
    echo "Response: $HEALTH_RESPONSE"
else
    echo "❌ API health check failed"
    echo "Response: $HEALTH_RESPONSE"
    echo ""
    echo "Showing API logs:"
    docker-compose logs api --tail 50
    exit 1
fi

echo ""
echo "======================================"
echo "✅ SYSTEM READY!"
echo "======================================"
echo ""
echo "📊 Available URLs:"
echo "  • API:    http://localhost:8000"
echo "  • Docs:   http://localhost:8000/docs"
echo "  • Flower: http://localhost:5555"
echo ""
echo "📝 View logs:"
echo "  docker-compose logs -f api"
echo "  docker-compose logs -f worker"
echo ""
echo "🧪 Test with sample data:"
echo "  python3 scripts/generate_sample_data.py --rows 1000 --output test.csv"
echo "  curl -X POST http://localhost:8000/api/v1/upload-transactions -F 'file=@test.csv'"
echo ""
