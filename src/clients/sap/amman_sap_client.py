import httpx
from src.clients.sap.sap_client_interface import SapClientInterface
from src.config import Config

# Define constants for expected SAP response fields
SAP_MSGTY_KEY = "Request.Msgty"
SAP_MSGCD_KEY = "Request.Msgcd"
SAP_MSGTX_KEY = "Request.Msgtx"

# Define constants for expected message codes
MSGCD_S = "0"  # Success code from SAP (adjust if different)
MSGCD_E_SYSTEM = "4"  # Generic System Error (adjust if different)


class AmmanSapClient(SapClientInterface):
    """
    SAP Client implementation for the AMMAN client.
    """

    def __init__(self, config: Config):
        self._config = config
        self._sap_service_url = self._config.AMMAN_RP_SAP_SERV
        self._sap_username = self._config.AMMAN_RP_SAP_USER
        self._sap_password = self._config.AMMAN_RP_SAP_PASS

        # Check if required config is available
        if not all([self._sap_service_url, self._sap_username, self._sap_password]):
            print("WARNING: Amman SAP client configuration is incomplete.")
            # Depending on severity, you might raise an error or handle gracefully

    async def reset_password(self, email: str, session_id: str) -> dict[str, any]:
        """
        Initiates the SAP password reset process for the AMMAN client.
        """
        print(
            f"--- AmmanSapClient: Initiating password reset to {self._sap_service_url}, with user {self._sap_username} ---")
        print(
            f"--- AmmanSapClient: Initiating password reset for {email}, session: {session_id} ---")

        if not all([self._sap_service_url, self._sap_username, self._sap_password]):
            print("ERROR: Amman SAP client not configured. Cannot perform reset.")
            # Return a standardized error response
            return {
                "status_code": None,
                "status_message": "Client Not Configured",
                "message_type": "E",
                "message_code": MSGCD_E_SYSTEM,
                "message_text": "SAP client configuration is missing."
            }
        auth_headers = httpx.BasicAuth(self._sap_username, self._sap_password)
        request_body = {
            "AppKey": self._config.MICROSOFT_APP_ID,
            "SessionId": session_id,
            "Email": email
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self._sap_service_url,
                    json=request_body,
                    auth=auth_headers,
                    timeout=30.0
                )
                print(
                    f"--- AmmanSapClient: Received SAP response status: {response.status_code} {response.reason_phrase} ---")
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

                # Parse the JSON response body
                response_body = response.json()
                print(
                    f"--- AmmanSapClient: SAP response body: {response_body} ---")

                # Extract SAP message details from the response body
                msgty = response_body.get("Request", {}).get("Msgty")
                msgcd = response_body.get("Request", {}).get("Msgcd")
                msgtx = response_body.get("Request", {}).get("Msgtx")

                print(
                    f"--- AmmanSapClient: SAP Message Type: {msgty}, Code: {msgcd}, Text: {msgtx} ---")

                # Return a standardized response dictionary
                return {
                    "status_code": str(response.status_code),
                    "status_message": response.reason_phrase,
                    "message_type": msgty,
                    "message_code": msgcd.strip() if msgcd else None,
                    "message_text": msgtx
                }
            except httpx.HTTPStatusError as e:
                # Handle HTTP errors (4xx or 5xx responses)
                print(
                    f"--- AmmanSapClient ERROR: HTTP error occurred: {e} ---")
                print(f"Response body: {e.response.text}")
                return {
                    "status_code": str(e.response.status_code),
                    "status_message": e.response.reason_phrase,
                    "message_type": "E",
                    "message_code": MSGCD_E_SYSTEM,
                    "message_text": f"SAP service returned an HTTP error: {e.response.status_code}"
                }
            except httpx.RequestError as e:
                # Handle network/request errors (timeout, connection failure, etc.)
                print(
                    f"--- AmmanSapClient ERROR: Request error occurred: {e} ---")
                return {
                    "status_code": None,
                    "status_message": "Request Failed",
                    "message_type": "E",  # Assume Error
                    "message_code": MSGCD_E_SYSTEM,  # Use generic system error code
                    "message_text": f"Failed to connect to SAP service: {e}"
                }
            except Exception as e:
                print(f"--- AmmanSapClient UNEXPECTED ERROR: {e} ---")
                import traceback
                traceback.print_exc()
                return {
                    "status_code": None,
                    "status_message": "Unexpected Error",
                    "message_type": "E",
                    "message_code": MSGCD_E_SYSTEM,
                    "message_text": f"An unexpected error occurred during SAP reset: {e}"
                }
