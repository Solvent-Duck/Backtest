# Backtest - Intervention Testing Platform

See if your interventions work.

## Overview

Backtest is an intervention testing platform that enables users to scientifically test whether their supplements, lifestyle changes, and biohacking interventions are actually working by automatically correlating interventions with objective health metrics from Apple Health.

## Features

- **Apple Health Integration**: Import data from any device that syncs to Apple Health (Oura, RingConn, Whoop, Apple Watch, etc.)
- **Intervention Tracking**: Log supplements, diet changes, exercise protocols, and more
- **Statistical Analysis**: Automated before/after comparison with significance testing
- **Timeline Visualization**: Interactive charts showing health metrics with intervention markers
- **Insight Generation**: Plain-language interpretation of results
- **Report Export**: Generate PDF reports for personal records or healthcare providers

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with TimescaleDB
- **Background Jobs**: Celery with Redis
- **Auth**: Supabase Auth
- **Storage**: Supabase Storage

### Frontend
- **Framework**: Next.js 14 (App Router) with TypeScript
- **Styling**: Tailwind CSS + Shadcn/ui
- **Visualization**: Recharts
- **State Management**: TanStack Query + Zustand
- **Hosting**: Vercel

## Project Structure

```
/workspace
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Core config, security
│   │   ├── models/   # Database models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   └── workers/  # Celery background tasks
│   ├── alembic/      # Database migrations
│   └── tests/        # Test suite
├── frontend/         # Next.js application
│   ├── app/          # App Router pages
│   ├── components/   # React components
│   ├── lib/          # Utilities
│   └── public/       # Static assets
└── docs/             # Documentation
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with TimescaleDB extension
- Redis

### 1. Clone and Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database and Redis URLs

# Initialize database
./scripts/init_db.sh  # Or follow manual setup in docs/SETUP.md

# Start backend server
uvicorn app.main:app --reload
```

### 2. Setup Frontend

```bash
cd frontend
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local - set NEXT_PUBLIC_API_URL=http://localhost:8000

# Start frontend
npm run dev
```

### 3. Start Celery Worker (for background jobs)

```bash
cd backend
source venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=info
```

### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## Getting Started

For detailed setup instructions, see [docs/SETUP.md](docs/SETUP.md).

For deployment instructions, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Development Status

This project is in active development following the MVP design document. Current focus: Foundation and core features (Weeks 1-4).

## License

See LICENSE file for details.
