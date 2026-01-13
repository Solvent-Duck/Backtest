"""
Database initialization script
Creates tables and sets up TimescaleDB
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine, Base
from app.core.config import settings


async def init_database():
    """Initialize database with tables and TimescaleDB setup"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Enable TimescaleDB extension
        if settings.TIMESCALEDB_ENABLED:
            print("Enabling TimescaleDB extension...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
            
            # Create hypertable
            try:
                print("Creating hypertable...")
                await conn.execute(text(
                    "SELECT create_hypertable('health_metrics', 'timestamp', "
                    "chunk_time_interval => INTERVAL '7 days', "
                    "if_not_exists => TRUE);"
                ))
                print("✓ Hypertable created")
            except Exception as e:
                print(f"Note: {e}")
            
            # Enable compression
            try:
                print("Enabling compression...")
                await conn.execute(text(
                    "ALTER TABLE health_metrics SET ("
                    "timescaledb.compress, "
                    "timescaledb.compress_segmentby = 'user_id, metric_type'"
                    ");"
                ))
                print("✓ Compression enabled")
            except Exception as e:
                print(f"Note: {e}")
            
            # Add compression policy
            try:
                print("Adding compression policy...")
                await conn.execute(text(
                    "SELECT add_compression_policy('health_metrics', INTERVAL '7 days', if_not_exists => TRUE);"
                ))
                print("✓ Compression policy added")
            except Exception as e:
                print(f"Note: {e}")
    
    print("\n✓ Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_database())
