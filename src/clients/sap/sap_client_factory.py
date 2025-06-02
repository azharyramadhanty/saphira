from src.clients.sap.sap_client_interface import SapClientInterface
from src.clients.sap.amman_sap_client import AmmanSapClient
from src.clients.sap.accenture_sap_client import AccentureSapClient
from src.config import Config

CLIENT_TYPE_AMMAN = "AMMAN"
CLIENT_TYPE_ACCENTURE = "ACCENTURE"


class SapClientFactory:
    """
    Factory for creating client-specific SAP client implementations.
    """

    def __init__(self, config: Config):
        self._config = config

    def get_sap_client(self, client_type: str) -> SapClientInterface | None:
        """
        Returns the appropriate SapClientInterface implementation for the given client type.
        Returns None if the client type is not supported for SAP interactions.
        """
        print(
            f"--- SapClientFactory: Getting SAP client for type: {client_type} ---")
        if client_type == CLIENT_TYPE_AMMAN:
            return AmmanSapClient(config=self._config)
        elif client_type == CLIENT_TYPE_ACCENTURE:
            return AccentureSapClient(config=self._config)

        print(
            f"--- SapClientFactory: No supported SAP client found for type: {client_type} ---")
        return None
