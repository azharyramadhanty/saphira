from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import app_config
from src.database.session import initialize_database_pool, close_database_pool
from src.api.routes import chatbot
from src.bots.bot_state_management import initialize_state_management, close_state_management


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load configuration from Key Vault (optional)
    print("Application startup: Loading configuration...")
    await app_config.load_secrets_from_keyvault()

    print("Initializing state management...")
    await initialize_state_management()
    print("State management initialized.")

    # Startup: Initialize database pool
    print("Initializing database pool...")
    await initialize_database_pool()
    print("Database pool initialized.")

    # Startup: Create database tables (Use migrations for production!)
    # await create_db_and_tables() # Uncomment if SQLModel to create tables on startup
    yield

    print("Shutting down database pool...")
    await close_database_pool()
    print("Database pool shut down.")
    print("Application shutdown complete.")

    print("Shutting down state management...")
    await close_state_management()
    print("State management shut down.")
    print("Application shutdown complete.")


# Create FastAPI app instance
app = FastAPI(lifespan=lifespan)

# Configure CORS middleware
# WARNING: allow_origins=["*"] is for local development/testing ONLY.
# Restrict this to specific origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your bot message router (will create this in the next step)
app.include_router(chatbot.router, prefix="/api")
# Endpoint to check if config loaded successfully (for debugging)


@app.get("/config")
async def get_app_config():
    """
    WARNING: Do NOT expose sensitive config details in a production endpoint!
    This is for local development debugging only.
    """
    return {
        "MICROSOFT_APP_ID": app_config.MICROSOFT_APP_ID,
        "MICROSOFT_APP_PASSWORD": app_config.MICROSOFT_APP_PASSWORD,
        "AZURE_STORAGE_CONNECTION_STRING": app_config.AZURE_STORAGE_CONNECTION_STRING,
        "AZURE_STORAGE_CONTAINER_NAME": app_config.AZURE_STORAGE_CONTAINER_NAME,
        "DB_SERV": app_config.DB_SERV,
        "DB_NAME": app_config.DB_NAME,
        "DB_USER": app_config.DB_USER,
        "DB_PASS": app_config.DB_PASS,
        "DB_PORT": app_config.DB_PORT,
        "AMMAN_RP_SAP_SERV": app_config.AMMAN_RP_SAP_SERV,
        "AMMAN_RP_SAP_USER": app_config.AMMAN_RP_SAP_USER,
        "AMMAN_RP_SAP_PASS": app_config.AMMAN_RP_SAP_PASS
    }

# from fastapi import FastAPI
# from contextlib import asynccontextmanager
# from src.db.session import init_db
# from src.api.routes import bands

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await init_db()
#     yield  # pause here until app shuts down, Everything before yield is run on app startup
#     # cleanup logic goes after yield, Everything after yield (if any) runs on app shutdown

# app = FastAPI(lifespan=lifespan)

# app.include_router(bands.router, prefix="/api/v1")
