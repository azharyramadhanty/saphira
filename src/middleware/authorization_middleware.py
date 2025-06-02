# bots/authorization_middleware.py
from botbuilder.core import Middleware, TurnContext
from botbuilder.schema import ActivityTypes
from src.services.domain_client_service import DomainClientService
from src.models.client import Client


class AuthorizationMiddleware(Middleware):
    """
    Middleware to check if the user's client type is authorized to use the bot.
    """

    def __init__(
        self,
        domain_client_service: DomainClientService
    ):
        self._domain_client_service = domain_client_service

    async def on_turn(self, context: TurnContext, next_logic):
        """
        Processes the turn activity to check for authorization.
        """
        print("--- Inside AuthorizationMiddleware.on_turn ---")
        if context.activity.type in [ActivityTypes.message, ActivityTypes.conversation_update]:
            # Need to inject service into TurnContext state
            # domain_client_service: DomainClientService = context.turn_state.get(
            #     "DomainClientService")
            if not self._domain_client_service:
                print(
                    "CRITICAL ERROR: DomainClientService not available in TurnContext.turn_state for AuthorizationMiddleware.")
                # Decide how to handle this critical error - maybe send an error message and stop
                await context.send_activity("An internal error occurred during authorization setup.")
                return  # Stop the pipeline

            # Determine the client type using the service
            # Need the user's email or ID from the activity
            activity = context.activity
            email = None  # Logic to get email from activity
            user_id = activity.from_property.id

            if hasattr(activity.from_property, 'email') and activity.from_property.email:
                email = activity.from_property.email
            elif (
                hasattr(activity.from_property, 'properties')
                and isinstance(activity.from_property.properties, dict)
                and 'email' in activity.from_property.properties
            ):
                email = activity.from_property.properties['email']
            if not email:
                email = (
                    activity.from_property.aad_object_id
                    if hasattr(activity.from_property, 'aad_object_id') and activity.from_property.aad_object_id
                    else activity.from_property.id
                )
                print(
                    f"WARNING: Email not directly available in activity for auth check. Using ID/AAD ID: {email}")

            # Use the service to determine client details based on email
            # Need to handle the test user mapping here as well for local testing
            TEST_USER_MAPPING = {
                "91a30296-1dc5-41a3-928a-438d598ab7a9": "felicia.suprajitno@accenture.com"
            }
            if user_id in TEST_USER_MAPPING:
                email = TEST_USER_MAPPING[user_id]

            # Use the service to determine client details
            client_details: Client | None = await self._domain_client_service.determine_client_details(email)
            if not client_details:
                await context.send_activity("This bot is specifically for Amman users. Your email domain is not recognized as belonging to the Amman client. Please contact your IT support if you believe this is an error.")
                return
            await next_logic()
        else:
            await next_logic()
