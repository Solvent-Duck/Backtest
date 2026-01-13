"""
Database configuration and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import event, text
from app.core.config import settings

# Create async engine
# Replace postgresql:// with postgresql+asyncpg:// for async support
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    database_url,
    echo=settings.ENVIRONMENT == "development",
    future=True,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def init_timescaledb():
    """Initialize TimescaleDB extension and create hypertable"""
    if settings.TIMESCALEDB_ENABLED:
        async with engine.begin() as conn:
            # Enable TimescaleDB extension
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
            
            # Create hypertable if it doesn't exist
            try:
                await conn.execute(text(
                    "SELECT create_hypertable('health_metrics', 'timestamp', "
                    "chunk_time_interval => INTERVAL '7 days', "
                    "if_not_exists => TRUE);"
                ))
            except Exception:
                # Hypertable might already exist or table doesn't exist yet
                pass
            
            # Enable compression
            try:
                await conn.execute(text(
                    "ALTER TABLE health_metrics SET ("
                    "timescaledb.compress, "
                    "timescaledb.compress_segmentby = 'user_id, metric_type'"
                    ");"
                ))
            except Exception:
                pass


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
