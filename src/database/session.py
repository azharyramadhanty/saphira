from typing import AsyncGenerator
import ssl
from urllib.parse import quote_plus
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from src.config import app_config
from src.database.base import Base
import src.models.model_relationships

async_engine: AsyncEngine = None
async_session_factory = None


async def initialize_database_pool():
    """Initializes the async database engine and session factory using loaded config."""
    global async_engine, async_session_factory  # Use global keyword to modify the module-level variables

    # Ensure config attributes are populated before building URL
    if not all([app_config.DB_USER, app_config.DB_PASS, app_config.DB_SERV, app_config.DB_PORT, app_config.DB_NAME]):
        print("CRITICAL ERROR: Database configuration not loaded. Cannot initialize pool.")
        # Decide how to handle failure - maybe raise an error or exit
        raise ValueError("Database configuration is missing.")

    # Build the async database connection URL
    # Use asyncpg for PostgreSQL
    DATABASE_URL = f"postgresql+asyncpg://{quote_plus(app_config.DB_USER)}:{quote_plus(app_config.DB_PASS)}@{app_config.DB_SERV}:{app_config.DB_PORT}/{app_config.DB_NAME}"
    # use for sqllite
    # DATABASE_URL = "sqlite:///db.sqlite"

    # Add SSL parameters if needed for Azure PostgreSQL Flexible Server
    # Create the async engine
    # echo=True for debugging SQL queries (turn off in production)
    ssl_context = ssl.create_default_context()
    async_engine = create_async_engine(
        DATABASE_URL,
        connect_args={"ssl": ssl_context},
        echo=True,
        future=True
    )

    # Create an async session factory
    # expire_on_commit=False is often needed with async sessions
    async_session_factory = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    print("Database engine and session factory created.")


async def close_database_pool():
    """Disposes the database engine."""
    if async_engine:
        print("Disposing database engine...")
        await async_engine.dispose()
        print("Database engine disposed.")
    else:
        print("Database engine was not initialized, no pool to dispose.")


async def create_db_and_tables():
    """Creates database tables based on SQLModel metadata."""
    try:
        if async_engine is None:
            raise RuntimeError(
                "Database engine not initialized. Call initialize_database_pool first.")
        print("Creating database tables (if they don't exist)...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables checked/created.")
    except Exception as e:
        print(f"ERROR: Could not create database during startup: {e}")
        raise


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to provide an async database session.
    Handles session lifecycle (creation, commit, rollback, closing).
    Ensures engine and factory are initialized.
    """
    if async_session_factory is None:
        raise RuntimeError(
            "Database session factory not initialized. Call initialize_database_pool first.")

    async with async_session_factory() as session:
        try:
            print("--- DB: Providing async session ---")
            yield session  # Provide the session to the endpoint/dependencies
            # If no exceptions occurred, commit the transaction
            # print("--- DB: Committing session changes")
            # await session.commit()
        except Exception as e:
            print(
                f"--- DB ERROR: Rolling back session changes due to exception: {e} ---")
            await session.rollback()
            # Re-raise the exception so FastAPI's error handling can catch it
            raise
        finally:
            print("--- DB: Closing async session ---")
            await session.close()
