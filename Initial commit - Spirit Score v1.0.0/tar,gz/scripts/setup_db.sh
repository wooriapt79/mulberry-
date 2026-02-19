#!/bin/bash

# Spirit Score Database Setup Script
# CTO Koda

set -e

echo "🌾 Spirit Score Database Setup"
echo "================================"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  Warning: .env file not found. Using defaults."
fi

DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-mulberry}
DB_USER=${DB_USER:-postgres}

echo ""
echo "📊 Database Configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL connection..."
if ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running on $DB_HOST:$DB_PORT"
    echo "   Please start PostgreSQL first."
    exit 1
fi
echo "✅ PostgreSQL is running"
echo ""

# Create database if it doesn't exist
echo "📦 Creating database '$DB_NAME'..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME"
echo "✅ Database ready"
echo ""

# Apply schema
echo "🏗️  Applying database schema..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database/db_schema.sql
echo "✅ Schema applied"
echo ""

# Verify tables
echo "🔍 Verifying tables..."
TABLE_COUNT=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
echo "   Found $TABLE_COUNT tables"

if [ "$TABLE_COUNT" -ge 6 ]; then
    echo "✅ All tables created successfully"
else
    echo "⚠️  Warning: Expected at least 6 tables, found $TABLE_COUNT"
fi

echo ""
echo "🎉 Database setup complete!"
echo ""
echo "Next steps:"
echo "  1. Update .env with your database credentials"
echo "  2. Run: python src/api.py"
echo "  3. Visit: http://localhost:8000/docs"
echo ""
