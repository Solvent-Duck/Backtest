# Setup Guide

This guide will help you set up the Backtest intervention testing platform for local development.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with TimescaleDB extension
- Redis
- Git

## Backend Setup

### 1. Install Python Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Database

#### Install TimescaleDB

**macOS (Homebrew):**
```bash
brew install timescaledb
```

**Ubuntu/Debian:**
```bash
# Add TimescaleDB repository
sudo sh -c "echo 'deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main' > /etc/apt/sources.list.d/timescaledb.list"
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -
sudo apt-get update
sudo apt-get install timescaledb-2-postgresql-15
```

**PostgreSQL Setup:**
```bash
# Create database
createdb backtest

# Connect to PostgreSQL
psql backtest

# Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;
\q
```

### 3. Set Up Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

Update the following in `.env`:
- `DATABASE_URL`: Your PostgreSQL connection string
- `REDIS_URL`: Your Redis connection string
- `SECRET_KEY`: Generate a secure random key
- `SUPABASE_URL` and keys (if using Supabase for auth/storage)

### 5. Run Database Migrations

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 6. Set Up TimescaleDB Hypertable

After running migrations, connect to your database and run:

```sql
-- Convert health_metrics to hypertable
SELECT create_hypertable('health_metrics', 'timestamp', 
    chunk_time_interval => INTERVAL '7 days');

-- Enable compression
ALTER TABLE health_metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'user_id, metric_type'
);

-- Add compression policy (compress data older than 7 days)
SELECT add_compression_policy('health_metrics', INTERVAL '7 days');

-- Create continuous aggregate for daily metrics
CREATE MATERIALIZED VIEW daily_metrics
WITH (timescaledb.continuous) AS
SELECT 
    user_id,
    metric_type,
    time_bucket('1 day', timestamp) AS day,
    AVG(value) as avg_value,
    STDDEV(value) as stddev_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as sample_size
FROM health_metrics
GROUP BY user_id, metric_type, day;

-- Auto-refresh policy
SELECT add_continuous_aggregate_policy('daily_metrics',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 hour');
```

### 7. Start Backend Server

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Start Celery Worker (in separate terminal)

```bash
celery -A app.workers.celery_app worker --loglevel=info
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

```bash
cp .env.local.example .env.local
# Edit .env.local with your configuration
```

Update `NEXT_PUBLIC_API_URL` to point to your backend (default: `http://localhost:8000`)

### 3. Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Testing the Setup

### 1. Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/api/docs
```

### 2. Test Frontend

1. Open `http://localhost:3000`
2. Navigate to Dashboard
3. Create a test intervention
4. Upload a sample Apple Health export

### 3. Test Data Import

You can test with a sample Apple Health XML file. The parser expects the standard Apple Health export format.

## Development Workflow

1. **Backend changes**: The server auto-reloads on file changes
2. **Frontend changes**: Next.js hot-reloads automatically
3. **Database changes**: Create new migrations with `alembic revision --autogenerate`
4. **Background jobs**: Monitor Celery worker logs for processing status

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `pg_isready`
- Check connection string in `.env`
- Ensure TimescaleDB extension is installed: `psql -d backtest -c "SELECT * FROM pg_extension WHERE extname = 'timescaledb';"`

### Redis Connection Issues

- Verify Redis is running: `redis-cli ping` (should return `PONG`)
- Check Redis URL in `.env`

### Import Processing Fails

- Check Celery worker logs
- Verify file permissions on temp storage directory
- Check database connection in worker

### Frontend Can't Connect to Backend

- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Check CORS settings in backend `config.py`

## Next Steps

- Set up authentication (Supabase Auth)
- Configure file storage (Supabase Storage or S3)
- Set up monitoring (Sentry)
- Deploy to production
