from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, asc
from src.models.contact import Contact


class ContactRepository:
    """
    Repository for accessing Contact data from the database asynchronously.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def select_distinct_streams(
        self, client_id: str
    ) -> list[str]:
        """
        Selects distinct Contact streams for a client.
        Orders by stream.
        """
        query = (
            select(Contact.stream)
            .where(Contact.client_id == client_id)
            .distinct()
            .order_by(asc(Contact.stream))
        )
        result = await self.session.exec(query)
        return result.all()

    async def select_all_by_stream_or_substream(
        self,
        client_id: str,
        stream: str,
        sub_stream: str | None = None
    ) -> list[Contact]:
        """
        Selects Contact information for a specific client, stream, and optional sub-stream.
        Orders by stream, sub_stream, contact_name.
        """
        query = (
            select(Contact)
            .where(Contact.client_id == client_id)
            .where(Contact.stream == stream)
        )

        if sub_stream:
            query = query.where(Contact.sub_stream == sub_stream)

        query = query.order_by(
            Contact.stream, Contact.sub_stream, Contact.contact_name)

        result = await self.session.exec(query)
        return result.all()
