# Deployment Guide

This guide covers deploying Backtest to production environments.

## Backend Deployment

### Option 1: Railway

1. **Create Railway Account**
   - Sign up at [railway.app](https://railway.app)

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo" (or use Railway CLI)

3. **Add Services**
   - **PostgreSQL**: Add PostgreSQL service, enable TimescaleDB extension
   - **Redis**: Add Redis service
   - **Backend**: Deploy from GitHub or use Railway CLI

4. **Configure Environment Variables**
   - Add all variables from `.env.example`
   - Railway provides `DATABASE_URL` and `REDIS_URL` automatically

5. **Deploy**
   - Railway auto-deploys on git push
   - Or use: `railway up`

### Option 2: Render

1. **Create Render Account**
   - Sign up at [render.com](https://render.com)

2. **Create Services**
   - **PostgreSQL**: Create PostgreSQL database, enable TimescaleDB
   - **Redis**: Create Redis instance
   - **Web Service**: Create new Web Service from GitHub

3. **Configure**
   - Build command: `pip install -r requirements.txt && alembic upgrade head`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables

### Database Setup in Production

After deployment, connect to production database and run TimescaleDB setup:

```sql
-- Enable TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Convert to hypertable
SELECT create_hypertable('health_metrics', 'timestamp', 
    chunk_time_interval => INTERVAL '7 days');

-- Enable compression
ALTER TABLE health_metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'user_id, metric_type'
);

-- Add compression policy
SELECT add_compression_policy('health_metrics', INTERVAL '7 days');

-- Create continuous aggregate
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

### Celery Worker Deployment

**Railway:**
- Create separate service for Celery worker
- Start command: `celery -A app.workers.celery_app worker --loglevel=info`

**Render:**
- Create Background Worker service
- Start command: `celery -A app.workers.celery_app worker --loglevel=info`

## Frontend Deployment

### Vercel (Recommended)

1. **Connect Repository**
   - Sign up at [vercel.com](https://vercel.com)
   - Import GitHub repository

2. **Configure**
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

3. **Environment Variables**
   - Add `NEXT_PUBLIC_API_URL` pointing to backend
   - Add Supabase keys if using

4. **Deploy**
   - Vercel auto-deploys on push to main
   - Or trigger manual deployment

### Alternative: Netlify

1. **Connect Repository**
   - Sign up at [netlify.com](https://netlify.com)
   - Import from GitHub

2. **Configure**
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/.next`

3. **Environment Variables**
   - Add in Netlify dashboard

## Environment Variables Checklist

### Backend

- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `REDIS_URL` - Redis connection string
- [ ] `SECRET_KEY` - Secure random key
- [ ] `SUPABASE_URL` - Supabase project URL
- [ ] `SUPABASE_ANON_KEY` - Supabase anon key
- [ ] `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- [ ] `CORS_ORIGINS` - Allowed frontend origins
- [ ] `ENVIRONMENT` - Set to `production`
- [ ] `SENTRY_DSN` - Sentry error tracking (optional)

### Frontend

- [ ] `NEXT_PUBLIC_API_URL` - Backend API URL
- [ ] `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anon key

## Monitoring Setup

### Sentry

1. Create Sentry project
2. Add DSN to backend `.env`
3. Errors will automatically be tracked

### Uptime Monitoring

- Use UptimeRobot, Pingdom, or similar
- Monitor backend health endpoint: `/health`
- Monitor frontend URL

## Security Checklist

- [ ] Use HTTPS for all services
- [ ] Set secure `SECRET_KEY` (32+ random characters)
- [ ] Configure CORS to only allow your frontend domain
- [ ] Enable database SSL connections
- [ ] Set up rate limiting (if not using managed service)
- [ ] Configure file upload size limits
- [ ] Set up automated backups for database
- [ ] Enable database connection pooling
- [ ] Use environment variables for all secrets
- [ ] Enable security headers (CSP, HSTS, etc.)

## Performance Optimization

1. **Database**
   - Enable TimescaleDB compression
   - Use continuous aggregates for fast queries
   - Set up read replicas if needed

2. **Backend**
   - Enable gzip compression (already configured)
   - Use connection pooling
   - Cache analysis results in Redis

3. **Frontend**
   - Enable Next.js image optimization
   - Use CDN for static assets
   - Implement proper caching headers

## Backup Strategy

1. **Database Backups**
   - Automated daily backups (most providers include this)
   - Test restore procedure monthly

2. **File Storage**
   - Enable versioning if using S3/R2
   - Regular backups of uploaded files

## Scaling Considerations

### When to Scale

- **Database**: When query times exceed 500ms
- **Backend**: When response times exceed 1s
- **Workers**: When job queue grows >100 pending jobs

### Scaling Steps

1. **Database**
   - Add read replicas
   - Increase connection pool size
   - Optimize slow queries

2. **Backend**
   - Horizontal scaling (multiple instances)
   - Load balancer
   - Auto-scaling based on CPU/memory

3. **Workers**
   - Add more worker instances
   - Separate queues by priority

## Post-Deployment

1. **Verify**
   - Test all API endpoints
   - Test file upload
   - Test analysis generation
   - Monitor error logs

2. **Documentation**
   - Update API documentation
   - Document any custom configurations

3. **Monitoring**
   - Set up alerts for errors
   - Monitor performance metrics
   - Track user metrics
