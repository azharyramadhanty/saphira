from abc import ABC, abstractmethod


class SapClientInterface(ABC):
    """
    Abstract Base Class defining the interface for SAP client interactions.
    """

    @abstractmethod
    async def reset_password(self, email: str, session_id: str) -> dict[str, any]:
        """
        Initiates the SAP password reset process.

        Args:
            email: The user's email address.
            session_id: The bot's session ID for logging.

        Returns:
            A dictionary containing the response from the SAP service,
            including status code, message type, code, and text.
            Returns a standard error structure if the API call fails.
        """
        pass
