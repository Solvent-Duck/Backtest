#!/bin/bash
# Database initialization script

set -e

echo "Setting up Backtest database..."

# Check if database exists
if psql -lqt | cut -d \| -f 1 | grep -qw backtest; then
    echo "Database 'backtest' already exists"
else
    echo "Creating database 'backtest'..."
    createdb backtest
fi

# Connect and set up TimescaleDB
echo "Setting up TimescaleDB extension..."
psql -d backtest -c "CREATE EXTENSION IF NOT EXISTS timescaledb;" || {
    echo "ERROR: TimescaleDB extension not available. Please install TimescaleDB first."
    exit 1
}

echo "Running Alembic migrations..."
cd "$(dirname "$0")/.."
alembic upgrade head

echo "Setting up TimescaleDB hypertable and aggregates..."
psql -d backtest -f scripts/setup_timescaledb.sql

echo "Database setup complete!"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your DATABASE_URL"
echo "2. Start the backend server: uvicorn app.main:app --reload"
echo "3. Start Celery worker: celery -A app.workers.celery_app worker --loglevel=info"
