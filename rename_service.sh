#!/bin/bash

# Script to rename the service across all files

echo "======================================"
echo "🏷️  SERVICE RENAME UTILITY"
echo "======================================"
echo ""
echo "Current names:"
echo "  - Display: Sales Analytics API"
echo "  - Containers: sales_*"
echo "  - Project: analysis-basket"
echo ""
echo "Suggested names:"
echo "  1. SalesFlow Analytics (recommended)"
echo "  2. TransactStream API"
echo "  3. SalesInsight Hub"
echo "  4. VentaCore Analytics"
echo "  5. RetailFlow API"
echo "  6. Custom (enter your own)"
echo ""
read -p "Select option (1-6): " option

case $option in
    1)
        NEW_NAME="SalesFlow Analytics"
        NEW_SLUG="salesflow-analytics"
        NEW_PREFIX="salesflow"
        ;;
    2)
        NEW_NAME="TransactStream API"
        NEW_SLUG="transactstream-api"
        NEW_PREFIX="transactstream"
        ;;
    3)
        NEW_NAME="SalesInsight Hub"
        NEW_SLUG="salesinsight-hub"
        NEW_PREFIX="salesinsight"
        ;;
    4)
        NEW_NAME="VentaCore Analytics"
        NEW_SLUG="ventacore-analytics"
        NEW_PREFIX="ventacore"
        ;;
    5)
        NEW_NAME="RetailFlow API"
        NEW_SLUG="retailflow-api"
        NEW_PREFIX="retailflow"
        ;;
    6)
        read -p "Enter display name (e.g., 'My Sales API'): " NEW_NAME
        read -p "Enter slug (e.g., 'my-sales-api'): " NEW_SLUG
        read -p "Enter container prefix (e.g., 'mysales'): " NEW_PREFIX
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "Will rename to:"
echo "  - Display Name: $NEW_NAME"
echo "  - Project Slug: $NEW_SLUG"
echo "  - Container Prefix: $NEW_PREFIX"
echo ""
read -p "Proceed? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "Cancelled"
    exit 0
fi

echo ""
echo "🔄 Updating files..."

# Update app/core/config.py
sed -i.bak "s/APP_NAME: str = Field(default=\"Sales Analytics API\"/APP_NAME: str = Field(default=\"$NEW_NAME\"/" app/core/config.py
echo "✅ Updated app/core/config.py"

# Update docker-compose.yml container names
sed -i.bak "s/container_name: sales_/container_name: ${NEW_PREFIX}_/g" docker-compose.yml
echo "✅ Updated docker-compose.yml"

# Update README.md
sed -i.bak "s/Sales Analytics API/$NEW_NAME/g" README.md
sed -i.bak "s/analysis-basket/$NEW_SLUG/g" README.md
sed -i.bak "s/sales_/${NEW_PREFIX}_/g" README.md
echo "✅ Updated README.md"

# Update TESTING.md
sed -i.bak "s/Sales Analytics API/$NEW_NAME/g" TESTING.md
sed -i.bak "s/sales_/${NEW_PREFIX}_/g" TESTING.md
echo "✅ Updated TESTING.md"

# Update PROJECT_SUMMARY.md
sed -i.bak "s/Sales Analytics API/$NEW_NAME/g" PROJECT_SUMMARY.md
sed -i.bak "s/analysis-basket/$NEW_SLUG/g" PROJECT_SUMMARY.md
echo "✅ Updated PROJECT_SUMMARY.md"

# Update POSTMAN_EXAMPLES.md
sed -i.bak "s/Sales Analytics API/$NEW_NAME/g" POSTMAN_EXAMPLES.md
echo "✅ Updated POSTMAN_EXAMPLES.md"

# Update app/__init__.py
sed -i.bak "s/Sales Analytics API/$NEW_NAME/" app/__init__.py
echo "✅ Updated app/__init__.py"

# Remove backup files
find . -name "*.bak" -delete

echo ""
echo "======================================"
echo "✅ RENAME COMPLETE!"
echo "======================================"
echo ""
echo "📝 Next steps:"
echo "  1. Review the changes: git diff"
echo "  2. Rebuild containers: docker-compose down && docker-compose build"
echo "  3. Restart: docker-compose up -d"
echo ""
echo "🔧 To rename the directory itself:"
echo "  cd .."
echo "  mv analysis-basket $NEW_SLUG"
echo "  cd $NEW_SLUG"
echo ""
