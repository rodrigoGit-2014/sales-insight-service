#!/bin/bash
# Script para reconstruir y reiniciar los servicios con las correcciones aplicadas

echo "🛑 Deteniendo servicios actuales..."
docker-compose down

echo ""
echo "🧹 Limpiando imágenes antiguas (opcional pero recomendado)..."
docker-compose down -v

echo ""
echo "🔨 Reconstruyendo imágenes con código corregido..."
docker-compose build --no-cache

echo ""
echo "🚀 Iniciando servicios..."
docker-compose up -d

echo ""
echo "⏳ Esperando 5 segundos para que los servicios inicien..."
sleep 5

echo ""
echo "✅ Verificando estado de los servicios..."
docker-compose ps

echo ""
echo "🏥 Probando health check..."
curl http://localhost:8000/health

echo ""
echo ""
echo "📊 URLs disponibles:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Flower: http://localhost:5555"

echo ""
echo "📝 Ver logs en tiempo real:"
echo "  docker-compose logs -f api"
echo "  docker-compose logs -f worker"
