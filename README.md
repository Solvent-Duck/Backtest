# Intervention Testing Platform

A platform for testing health interventions (supplements, lifestyle changes) by automatically correlating them with objective health metrics from Apple Health.

## Features

- **Apple Health Integration**: Import data from Apple Health exports (supports all devices that sync to Apple Health)
- **Intervention Tracking**: Log supplements, diet changes, exercise protocols, and more
- **Statistical Analysis**: Automated before/after analysis with significance testing
- **Timeline Visualization**: Interactive charts showing metrics over time
- **Insight Generation**: Plain-language interpretation of results

## Tech Stack

### Backend
- **FastAPI** (Python 3.11+) - Async API framework
- **PostgreSQL + TimescaleDB** - Time-series optimized database
- **Celery + Redis** - Background job processing
- **lxml** - Efficient XML parsing for Apple Health exports
- **scipy** - Statistical analysis

### Frontend
- **Next.js 14** (App Router) - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Shadcn/ui** - UI components
- **Recharts** - Data visualization
- **TanStack Query** - Data fetching

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with TimescaleDB extension
- Redis

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database:
```bash
python scripts/init_db.py
```

6. Run development server:
```bash
uvicorn app.main:app --reload --port 8000
```

7. Run Celery worker (in separate terminal):
```bash
celery -A celery_app worker --loglevel=info
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.local.example .env.local
# Edit .env.local with your configuration
```

4. Run development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Configuration and database
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── tasks/        # Celery tasks
│   │   └── utils/        # Utility functions
│   ├── scripts/          # Utility scripts
│   └── requirements.txt
├── frontend/
│   ├── app/              # Next.js app directory
│   ├── components/       # React components
│   ├── lib/              # Utilities and API client
│   └── package.json
└── README.md
```

## API Endpoints

### Interventions
- `POST /api/v1/interventions` - Create intervention
- `GET /api/v1/interventions` - List interventions
- `GET /api/v1/interventions/{id}` - Get intervention
- `PATCH /api/v1/interventions/{id}` - Update intervention
- `DELETE /api/v1/interventions/{id}` - Delete intervention

### Health Data
- `POST /api/v1/health-data/upload` - Upload Apple Health export
- `GET /api/v1/health-data/imports` - List imports
- `GET /api/v1/health-data/imports/{id}` - Get import status
- `GET /api/v1/health-data/metrics` - Get daily metrics

### Analysis
- `POST /api/v1/analysis/interventions/{id}` - Run analysis
- `GET /api/v1/analysis/interventions/{id}/results` - Get results

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Deployment

See deployment documentation in the design document for production setup instructions.

## License

See LICENSE file.

## Contributing

This is an MVP project. See the design document for roadmap and feature plans.
