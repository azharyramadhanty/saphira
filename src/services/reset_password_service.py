from sqlmodel.ext.asyncio.session import AsyncSession
from src.clients.sap.sap_client_interface import SapClientInterface
from src.clients.sap.sap_client_factory import SapClientFactory
from src.services.log_service import LogService
from src.models.log_reset_password import LogResetPassword
from src.models.client import Client
from src.clients.sap.amman_sap_client import MSGCD_S, MSGCD_E_SYSTEM


class ResetPasswordService:
    """
    Service layer for handling SAP password reset business logic.
    Orchestrates SAP client interactions and logging.
    """

    def __init__(self, sap_client_factory: SapClientFactory, log_service: LogService):
        self._sap_client_factory = sap_client_factory
        self._log_service = log_service

    async def initiate_sap_password_reset(
        self,
        user_email: str,
        session_id: str,
        client_details: Client | None,
        session: AsyncSession
    ) -> dict[str, any]:
        """
        Initiates the SAP password reset process for the user.
        Selects the correct SAP client based on user's client type.
        Logs the reset request and response.
        """
        print(
            f"--- ResetPasswordService: Initiating SAP password reset for email: {user_email}, session: {session_id} ---")

        client_id = client_details.client_id if client_details else "UNKNOWN"

        # Select the correct SAP client implementation using the factory
        sap_client: SapClientInterface | None = self._sap_client_factory.get_sap_client(
            client_id)

        sap_response: dict[str, any] = {}
        if sap_client:
            sap_response = await sap_client.reset_password(user_email, session_id)
            print(
                f"--- ResetPasswordService: SAP client returned: {sap_response} ---")
        else:
            # Return error response if no client found
            sap_response = {
                "status_code": None,
                "status_message": "Client Not Supported",
                "message_type": "E",
                "message_code": MSGCD_E_SYSTEM,
                "message_text": f"SAP reset is not supported for client: {client_id}"
            }

        # Log the reset password attempt and its result
        log_entry = LogResetPassword(
            session_id=session_id,
            email=user_email,
            client_id=client_id,
            status_code=sap_response.get("status_code"),
            status_message=sap_response.get("status_message"),
            message_type=sap_response.get("message_type"),
            message_code=sap_response.get("message_code"),
            message_text=sap_response.get("message_text")
        )
        await self._log_service.log_reset_password(log_entry, session)
        print(f"--- ResetPasswordService: Reset Password log inserted ---")

        # Return a standardized result dictionary based on SAP message code
        # This will be used by the Agno tool to formulate the response
        result_code = sap_response.get("message_code", MSGCD_E_SYSTEM)
        result_text = sap_response.get("message_text", "An error occurred.")

        # Map SAP message codes to internal result types if needed
        # For now, just return the code and text
        return {
            "code": result_code,
            "text": result_text,
            "raw_sap_response": sap_response  # Include raw response for debugging
        }
