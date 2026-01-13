# Quick Start Guide

Get the Intervention Testing Platform running locally in minutes.

## Prerequisites

- Docker and Docker Compose installed
- OR Python 3.11+, Node.js 18+, PostgreSQL 15+ with TimescaleDB, and Redis

## Option 1: Docker Compose (Recommended)

1. **Start all services:**
```bash
docker-compose up -d
```

2. **Initialize the database:**
```bash
docker-compose exec backend python scripts/init_db.py
```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. **View logs:**
```bash
docker-compose logs -f
```

5. **Stop services:**
```bash
docker-compose down
```

## Option 2: Manual Setup

### Backend

1. **Navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your database and Redis URLs
```

5. **Initialize database:**
```bash
python scripts/init_db.py
```

6. **Start API server:**
```bash
python run.py
# Or: uvicorn app.main:app --reload
```

7. **Start Celery worker (new terminal):**
```bash
celery -A celery_app worker --loglevel=info
```

### Frontend

1. **Navigate to frontend:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Configure environment:**
```bash
cp .env.local.example .env.local
# Edit .env.local with your API URL
```

4. **Start development server:**
```bash
npm run dev
```

## Testing the Setup

1. **Check API health:**
```bash
curl http://localhost:8000/health
```

2. **Create a test intervention:**
```bash
curl -X POST http://localhost:8000/api/v1/interventions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Magnesium",
    "category": "supplement",
    "start_date": "2025-01-01",
    "baseline_days": 14
  }'
```

3. **Upload Apple Health data:**
   - Export your Apple Health data from iPhone (Settings > Health > Export All Health Data)
   - Use the upload endpoint or the dashboard UI

## Next Steps

- See README.md for full documentation
- Review the design document for feature roadmap
- Check API documentation at http://localhost:8000/docs

## Troubleshooting

**Database connection errors:**
- Ensure PostgreSQL is running and TimescaleDB extension is installed
- Check DATABASE_URL in .env file

**Redis connection errors:**
- Ensure Redis is running
- Check REDIS_URL in .env file

**Import errors:**
- Check file size (max 500MB)
- Ensure file is valid Apple Health export (.zip or .xml)
- Check Celery worker logs for processing errors
