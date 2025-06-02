from src.repositories.log_repository import LogRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.log_reset_password import LogResetPassword


class LogService:
    """
    Service layer for handling All Log operations.
    """

    def __init__(self, log_repo: LogRepository):
        self._log_repo = log_repo

    async def log_reset_password(self, log_rp: LogResetPassword, session: AsyncSession):
        """
        Logs a reset password attempt and commits the session for this DML.
        Receives the session from the caller.
        """
        print("--- LogService: Logging reset password attempt ---")
        await self._log_repo.insert_log_reset_password(log_rp)
        print("--- LogService: Committing session for log entry ---")
        await session.commit()

    # Add similar methods for logging general interactions or FAQ interactions if they are logged at specific points
    # async def log_general_interaction(self, log_entry: Log, session: AsyncSession): ...
    # async def log_faq_lookup(self, log_faq_entry: LogFaq, session: AsyncSession): ...
