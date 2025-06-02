from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from botbuilder.core import TurnContext, BotFrameworkAdapter, BotFrameworkAdapterSettings, AutoSaveStateMiddleware
from src.config import app_config, Config
from src.database.session import get_async_session
from src.bots.saphira_activity_handler import SaphiraActivityHandler
from src.repositories.contact_repository import ContactRepository
from src.repositories.faq_repository import FaqRepository
from src.repositories.object_repository import ObjectRepository
from src.repositories.domain_client_repository import DomainClientRepository
from src.repositories.log_repository import LogRepository
from src.services.contact_service import ContactService
from src.services.domain_client_service import DomainClientService
from src.services.reset_password_service import ResetPasswordService
from src.services.log_service import LogService
from src.services.faq_service import FaqService
from src.clients.sap.sap_client_factory import SapClientFactory
from src.middleware.authorization_middleware import AuthorizationMiddleware
from src.bots.bot_state_management import StateAccessorMiddleware, ConversationState, UserState, get_conversation_state, get_user_state

"""
the wiring diagram that defines how instances of the adapter, handler, state accessors, database sessions, and later, all services and AI components are created and provided to the parts of the application (like the /api/messages endpoint) that need them.
"""


def get_config():  # Dependency function for configuration
    """Provides the application configuration."""
    return app_config


# Dependency function for async database session
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides an async database session."""
    async for session in get_async_session():
        yield session


def get_domain_client_repository(session: AsyncSession = Depends(get_db_session)) -> DomainClientRepository:
    """Provides the DomainClientRepository instance with an injected session."""
    repo = DomainClientRepository(session=session)
    return repo


def get_domain_client_service(domain_client_repo: DomainClientRepository = Depends(get_domain_client_repository)) -> DomainClientService:
    """Provides the DomainClientService instance with an injected repository."""
    service = DomainClientService(domain_client_repo=domain_client_repo)
    return service


def get_authorization_middleware(
    domain_client_service: DomainClientService = Depends(
        get_domain_client_service)
) -> AuthorizationMiddleware:
    """Provides the AuthorizationMiddleware instance with injected dependencies."""
    print("--- Inside get_authorization_middleware ---")
    # middleware = AuthorizationMiddleware()
    # *** Need to pass the service to the middleware instance if its constructor accepts it ***
    # Let's update AuthorizationMiddleware __init__
    middleware = AuthorizationMiddleware(
        domain_client_service=domain_client_service)
    print("AuthorizationMiddleware instantiated.")
    return middleware


def get_bot_adapter(
    config: Config = Depends(get_config),
    conversation_state: ConversationState = Depends(get_conversation_state),
    user_state: UserState = Depends(get_user_state),
    auth_middleware: AuthorizationMiddleware = Depends(
        get_authorization_middleware)
) -> BotFrameworkAdapter:
    """Provides the Bot Framework Adapter."""
    print("--- Inside get_bot_adapter ---")
    adapter_settings = BotFrameworkAdapterSettings(
        config.MICROSOFT_APP_ID,
        config.MICROSOFT_APP_PASSWORD
    )
    adapter = BotFrameworkAdapter(adapter_settings)
    print("BotFrameworkAdapter instantiated with state objects.")

    async def on_turn_error(turn_context: TurnContext, error: Exception):
        print(f"\n [on_turn_error] unhandled error in bot: {error}")
        await turn_context.send_activity("The bot encountered an error or bug.")
        await turn_context.send_trace_activity(
            "OnTurnError Trace",
            f"{error}",
            "https://www.botframework.com/schemas/error",
            "TurnError"
        )
        try:
            await conversation_state.save_changes(turn_context, True)
            await user_state.save_changes(turn_context, True)
            print("[on_turn_error] State saved after error.")
        except Exception as save_error:
            print(f"[on_turn_error] Error saving state: {save_error}")

    adapter.on_turn_error = on_turn_error
    # *** ADD MIDDLEWARE IN ORDER OF EXECUTION ***
    # 1. Add State Accessors to TurnContext
    adapter.use(StateAccessorMiddleware())
    # 2. Authorization Middleware (Checks if user is authorized)
    adapter.use(auth_middleware)
    # 3. Auto-save State Middleware (Saves state if not stopped by auth)
    adapter.use(AutoSaveStateMiddleware([conversation_state, user_state]))
    print("--- Exiting get_bot_adapter ---")
    return adapter


def get_contact_repository(session: AsyncSession = Depends(get_db_session)) -> ContactRepository:
    """Provides the ContactRepository instance with an injected session."""
    repo = ContactRepository(session=session)
    return repo


def get_contact_service(contact_repo: ContactRepository = Depends(get_contact_repository)) -> ContactService:
    """Provides the ContactService instance with an injected repository."""
    service = ContactService(contact_repo=contact_repo)
    return service


def get_log_repository(session: AsyncSession = Depends(get_db_session)) -> LogRepository:
    """Provides the LogRepository instance with an injected session."""
    repo = LogRepository(session=session)
    return repo


def get_log_service(log_repo: LogRepository = Depends(get_log_repository)) -> LogService:
    """Provides the LogService instance with an injected session."""
    service = LogService(log_repo=log_repo)
    return service


def get_sap_client_factory(config: AsyncSession = Depends(get_config)) -> SapClientFactory:
    """Provides the SapClientFactory instance with an injected session."""
    factory = SapClientFactory(config=config)
    return factory


def get_reset_password_service(
    sap_client_factory: SapClientFactory = Depends(get_sap_client_factory),
    log_service: LogService = Depends(get_log_service)
) -> ResetPasswordService:
    """Provides the ResetPasswordService instance with injected dependencies."""
    service = ResetPasswordService(
        sap_client_factory=sap_client_factory,
        log_service=log_service
    )
    return service


def get_faq_repository(session: AsyncSession = Depends(get_db_session)) -> FaqRepository:
    """Provides the FaqRepository instance with an injected session."""
    repo = FaqRepository(session=session)
    return repo


def get_faq_service(faq_repo: FaqRepository = Depends(get_faq_repository)) -> FaqService:
    """Provides the LogService instance with an injected session."""
    service = FaqService(faq_repo=faq_repo)
    return service


def get_object_repository(session: AsyncSession = Depends(get_db_session)) -> ObjectRepository:
    """Provides the ObjectRepository instance with an injected session."""
    repo = ObjectRepository(session=session)
    return repo


def get_saphira_activity_handler(
    faq_service: FaqService = Depends(get_faq_service),
    contact_service: ContactService = Depends(get_contact_service),
    domain_client_service: DomainClientService = Depends(
        get_domain_client_service),
    reset_password_service: ResetPasswordService = Depends(
        get_reset_password_service),
    db_session: AsyncSession = Depends(get_db_session)
) -> SaphiraActivityHandler:
    """Provides the Saphira Activity Handler."""
    handler = SaphiraActivityHandler(
        faq_service=faq_service,
        contact_service=contact_service,
        domain_client_service=domain_client_service,
        reset_password_service=reset_password_service,
        db_session=db_session
        # agno_agent=agno_agent
    )
    return handler
