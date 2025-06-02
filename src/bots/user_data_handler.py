from typing import Dict, Any
from datetime import datetime
from botbuilder.core import TurnContext, StatePropertyAccessor
from src.models.user_data import UserData
from src.bots.bot_state_management import USER_STATE_ACCESSOR_KEY
from src.services.domain_client_service import DomainClientService
from src.models.client import Client


class UserDataHandler:
    """
    Helper class to manage user-specific state data and wrapper around the Bot Framework's UserStatePropertyAccessor for your "userData" state. Its role is to provide a more application-specific interface for interacting with user-related state data. Instead of directly calling await self._user_data_accessor.get(turn_context, {}) everywhere, you'll call methods on the UserDataHandler like user_data_handler.get_client_type(), user_data_handler.set_language(), user_data_handler.get_email(). It abstracts away the lower-level state accessor calls.
    """

    def __init__(self, turn_context: TurnContext, domain_client_service: DomainClientService):
        self.test_user_mapping = {
            "91a30296-1dc5-41a3-928a-438d598ab7a9": "felicia.suprajitno@accenture.com"
        }
        self._turn_context = turn_context
        self._user_data_accessor: StatePropertyAccessor = self._turn_context.turn_state.get(
            USER_STATE_ACCESSOR_KEY)
        if not self._user_data_accessor:
            print("CRITICAL ERROR: UserDataAccessor not found in TurnContext.turn_state")
        self._domain_client_service = domain_client_service

    async def get_user_data(self) -> UserData:
        """
        Retrieves the UserData from state. Returns a default UserData instance
        if the state does not exist in storage (get() returns None).
        """
        print("--- UserDataHandler: Attempting to get user state ---")
        user_data_dict = None
        user_data = None
        try:
            user_data_dict = await self._user_data_accessor.get(self._turn_context)
        except Exception as e:
            print(
                f"--- UserDataHandler UNEXPECTED ERROR during state GET: {e} ---")

        if user_data_dict is None:
            user_data = UserData()
        else:
            try:
                user_data = UserData(**user_data_dict)
            except Exception as e:
                print(
                    f"--- UserDataHandler ERROR deserializing state dictionary: {e} ---")
                user_data = UserData()
        return user_data

    async def set_user_data(self, user_data: UserData):
        try:
            await self._user_data_accessor.set(self._turn_context, user_data.model_dump())
        except Exception as e:
            print(
                f"--- UserDataHandler ERROR setting state in accessor: {e} ---")
            raise

    async def get_email(self) -> str | None:
        """Gets the user's email from state."""
        user_data = await self.get_user_data()
        return user_data.email

    async def set_email_from_activity(self):
        """Sets the user's email from the activity."""
        print("--- UserDataHandler: Setting email from activity ---")
        # Get the user's email from the activity (usually from the 'from' property)
        # In Teams, the 'from.aad_object_id' or 'from.email' might be available depending on channel config and user's org settings
        # The 'from.name' is usually the display name.
        # Access the original activity via TurnContext
        activity = self._turn_context.activity
        email = None
        # Common places to find email in Teams activity:
        # activity.from_property.email (may not always be populated)
        # activity.from_property.properties.get('email') (less common)
        # For Teams, the most reliable way to get user details often involves
        # using the TeamsInfo class and the TurnContext.
        # Example (requires botbuilder-dialogs-teams or similar):
        # from botbuilder.dialogs.teams import TeamsInfo
        # team_member = await TeamsInfo.get_member(self._turn_context, self._turn_context.activity.from_property.id)
        # email = team_member.email if team_member else None

        # For initial testing, let's see if activity.from_property.email is available
        print("start set email in user data handler")
        email = None
        if hasattr(activity.from_property, 'email') and activity.from_property.email:
            email = activity.from_property.email
        elif (
            hasattr(activity.from_property, 'properties')
            and isinstance(activity.from_property.properties, dict)
            and 'email' in activity.from_property.properties
        ):
            email = activity.from_property.properties['email']
        # Fallback or primary method for Teams: potentially lookup using the user ID
        # This would require interacting with the Teams channel API via the adapter
        # For now, let's just get a placeholder or the ID if email is not directly available

        # If email is not available, maybe use the user's AAD object ID or ID?
        if not email:
            email = (
                activity.from_property.aad_object_id
                if hasattr(activity.from_property, 'aad_object_id') and activity.from_property.aad_object_id
                else activity.from_property.id
            )
            print(
                f"WARNING: Email not directly available in activity. Using ID/AAD ID: {email}")
            # In a real scenario, you'd look up the user's email using their AAD ID or Teams ID from your backend DB or AAD
            # This might involve another service or a dependency injected into UserDataHandler
        user_data = await self.get_user_data()
        user_data.email = email.lower() if email else None
        await self.set_user_data(user_data)

    async def determine_and_set_client_type(self):
        """
        Determines the user's client type based on email domain lookup
        and saves it to state along with domain client details.
        """
        print("--- UserDataHandler: Determining and setting client type ---")
        email = await self.get_email()
        if not email:
            print("WARNING: Cannot determine client type, email is not available.")
            return

        user_id = self._turn_context.activity.from_property.id
        if user_id in self.test_user_mapping:
            email = self.test_user_mapping[user_id]
            print(
                f"--- UserDataHandler: Using test email mapping for user ID: {user_id} -> {email} ---")
            user_data = await self.get_user_data()
            user_data.email = email.lower()
            await self.set_user_data(user_data)

        client_type = "UNKNOWN"
        domain_client_details: dict[str, any] = {
            "client_id": "UNKNOWN",
            "client_name": "Unknown Client",
            "desk_name": "Support Desk",
            "desk_email": "support@example.com",
            "validity_start": None,
            "validity_end": None,
            "faq_example": "How can i help you?"
        }

        if email:
            client_from_db: Client | None = await self._domain_client_service.determine_client_details(email)
            if client_from_db:
                client_type = client_from_db.client_id
                domain_client_details = client_from_db.model_dump()

        user_data = await self.get_user_data()
        user_data.client_type = client_type
        user_data.domain_client_details = domain_client_details
        await self.set_user_data(user_data)

    async def get_client_type(self) -> str | None:
        """Gets the user's client type from state (e.g., ACCENTURE, AMMAN)."""
        user_data = await self.get_user_data()
        return user_data.client_type

    async def get_domain_client_details(self) -> Dict[str, Any] | None:
        """Gets the domain client details from state."""
        user_data = await self.get_user_data()
        return user_data.domain_client_details

    async def get_domain_client_details_model(self) -> Client | None:
        """
        Gets the domain client details from state as a Client model instance.
        Returns None if details are missing or client is UNKNOWN.
        """
        details_dict = await self.get_domain_client_details()
        if details_dict and details_dict.get("client_id") != "UNKNOWN":
            try:
                return Client(**details_dict)
            except Exception as e:
                print(
                    f"WARNING: Failed to deserialize domain client details from state to Client model: {e}")
                return None
        return None

    async def set_dialog_welcome_sent(self, sent: bool):
        """Sets the flag indicating if the welcome message has been sent."""
        print(f"--- UserDataHandler: Setting welcome sent flag to {sent} ---")
        user_data = await self.get_user_data()
        user_data.dialog_welcome_sent = sent
        await self.set_user_data(user_data)

    async def get_dialog_welcome_sent(self) -> bool:
        """Gets the flag indicating if the welcome message has been sent."""
        user_data = await self.get_user_data()
        return user_data.dialog_welcome_sent

    async def get_session_id(self) -> str | None:
        """Gets the current session ID from state."""
        user_data = await self.get_user_data()
        return user_data.session_id

    async def autogenerate_session_id(self):
        """Autogenerate the current session ID in state."""
        user_data = await self.get_user_data()
        today = datetime.now()
        email_part = user_data.email if user_data.email else self._turn_context.activity.from_property.id
        session_id = f"S_{today.strftime('%Y-%m-%d')}_{today.strftime('%H%M%S')}_{email_part}".upper()
        user_data.session_id = session_id
        await self.set_user_data(user_data)
        print(f"--- Generated new Session ID: {session_id} ---")

    # --- Add other getter/setter methods for UserData properties as needed ---
    # async def set_current_faq_question(self, question: str):
    #     user_data = await self.get_user_data()
    #     user_data.current_faq_question = question
    #     await self.set_user_data(user_data)

    # async def get_current_faq_question(self) -> Optional[str]:
    #     user_data = await self.get_user_data()
    #     return user_data.current_faq_question
