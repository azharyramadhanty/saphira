from src.repositories.domain_client_repository import DomainClientRepository
from src.models.client import Client


class DomainClientService:
    """
    Service layer for determining client type and retrieving domain client details.
    Depends on DomainClientRepository for database access.
    """

    def __init__(self, domain_client_repo: DomainClientRepository):
        self._domain_client_repo = domain_client_repo

    async def determine_client_details(self, email: str) -> Client | None:
        """
        Determines the user's client details based on email domain lookup.
        Returns None if no client is found for the email/domain.
        """
        # Call the repository method
        client_details = await self._domain_client_repo.select_domain_client_by_email(email)

        if client_details:
            print(
                f"--- DomainClientService: Client details: {client_details} ---")
            return client_details

        # If not found, try the domain part
        if "@" in email:
            _, domain = email.split("@")
            client_details = await self._domain_client_repo.select_domain_client_by_email(domain)
        print(f"--- DomainClientService: Client details: {client_details} ---")

        return client_details
