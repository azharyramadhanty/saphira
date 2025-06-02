from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_
from src.models.client import Client
from src.models.domain import Domain


class DomainClientRepository:
    """
    Repository for accessing Client data from the database asynchronously.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def select_domain_client_by_email(self, email: str) -> Client | None:
        """
        Selects Client details based on email (full email or domain part).
        """
        query = (
            select(Client)
            .join(
                Domain,
                and_(
                    Client.client_id == Domain.client_id
                ),
                isouter=True
            )
            .where(Domain.domain_id == email)
        )
        result = await self.session.exec(query)
        client = result.first()

        if client:
            return client

        return None
