-- TimescaleDB Setup Script
-- Run this after initial database migrations

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Convert health_metrics to hypertable
-- This enables time-series optimizations
SELECT create_hypertable('health_metrics', 'timestamp', 
    chunk_time_interval => INTERVAL '7 days');

-- Enable compression (90% storage reduction)
ALTER TABLE health_metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'user_id, metric_type'
);

-- Add compression policy (automatically compress data older than 7 days)
SELECT add_compression_policy('health_metrics', INTERVAL '7 days');

-- Create continuous aggregate for daily metrics
-- This pre-computes daily averages for fast queries
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

-- Auto-refresh policy for continuous aggregate
-- Updates aggregate hourly for recent data
SELECT add_continuous_aggregate_policy('daily_metrics',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 hour');

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_daily_metrics_user_type_day 
ON daily_metrics(user_id, metric_type, day);

-- Optional: Retention policy (delete data older than 5 years)
-- Uncomment if you want automatic data cleanup
-- SELECT add_retention_policy('health_metrics', INTERVAL '5 years');
