from src.repositories.contact_repository import ContactRepository
from src.models.contact import Contact


class ContactService:
    """
    Service layer for handling Contact-related business logic.
    Depends on ContactRepository for database access.
    """

    def __init__(self, contact_repo: ContactRepository):
        self._contact_repo = contact_repo

    async def get_all_streams(self, client_id: str) -> list[str]:
        """Retrieves a list of available contact streams for a given client."""
        return await self._contact_repo.select_distinct_streams(client_id)

    async def select_all_by_stream_and_substream(
        self,
        client_id: str,
        stream: str,
        sub_stream: str | None = None
    ) -> list[Contact]:
        """Retrieves all contact by stream and/or sub stream."""
        contacts = await self._contact_repo.select_all_by_stream_or_substream(client_id, stream, sub_stream)
        # Optional: If you need to check if there are multiple sub-streams
        # under this main stream, you might need another repo method or logic here.
        # The Node.js code seemed to check if selectContact with stream only returned > 1 row,
        # then marked as 'multiple_contact'. That logic might be better in the tool
        # or a data preparation step after calling this service.
        return contacts

    async def find_stream_from_text(self, client_id: str, text: str) -> str | None:
        """Attempts to find a stream name mentioned in the text."""
        available_streams = await self._contact_repo.select_distinct_streams(client_id)
        # Implement simple string matching or fuzzy matching here
        # Example: check if any available stream name is in the text
        for stream in available_streams:
            if stream.lower() in text.lower():
                return stream
        return None
