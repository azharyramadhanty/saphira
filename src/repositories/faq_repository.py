from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_
from src.models.faq import Faq
from src.models.object import Object
from src.models.verb import Verb
from src.models.contact import Contact


class FaqRepository:
    """
    Repository for accessing FAQ
    from the database asynchronously.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def select_faq_with_object_details(
        self, client_id: str
    ) -> list[Faq]:
        """
        Selects FAQs and eager loads related Object details using a join.
        (Simplified query, not including FTS or verb/additional_tag logic yet)
        """
        query = (
            select(Faq)
            .join(
                Object,
                and_(
                    Object.object_id == Faq.object_id,
                    Object.client_id == Faq.client_id
                ),
                isouter=True
            )
            .where(Faq.client_id == client_id)
        )
        result = await self.session.exec(query)
        return result.all()

    # --- Methods for inserting logs (Log, LogFaq, LogResetPassword) ---
    # async def insert_log(self, log_entry: Log):
    #     """Inserts a general log entry."""
    #     self.session.add(log_entry)
    #     # Note: Changes are committed when the session is committed,
    #     # which will likely happen at the end of the turn via the DI session yield.
    #     # await self.session.commit() # Only call commit if managing session lifespan differently

    # async def insert_log_faq(self, log_faq_entry: LogFaq):
    #     """Inserts an FAQ log entry."""
    #     self.session.add(log_faq_entry)

    # async def insert_log_reset_password(self, log_rp_entry: LogResetPassword):
    #     """Inserts a Reset Password log entry."""
    #     self.session.add(log_rp_entry)

    # # --- Method for updating logs (e.g., FAQ feedback) ---
    # async def update_log_faq_feedback(self, session_id: str, feedback: str):
    #     """Updates FAQ feedback for a log entry by session ID."""
    #     # Find the log entry(s) for the session
    #     query = select(LogFaq).where(LogFaq.session_id == session_id)
    #     result = await self.session.exec(query)
    #     log_entries = result.scalars().all() # Get all matches

    #     # Update feedback for found entries (assuming session_id uniquely identifies the relevant entry for feedback)
    #     for log_entry in log_entries:
    #         log_entry.faq_feedback = feedback
    #         self.session.add(log_entry) # Re-add to session to mark as modified
