from sqlmodel.ext.asyncio.session import AsyncSession
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount
from src.bots.user_data_handler import UserDataHandler
from src.services.contact_service import ContactService
from src.services.domain_client_service import DomainClientService
from src.services.reset_password_service import ResetPasswordService
from src.services.faq_service import FaqService


class SaphiraActivityHandler(ActivityHandler):
    """
    The ActivityHandler is the core class in the Bot Framework SDK that receives incoming activities (messages, member added/removed, typing, etc.) from the adapter and routes them to specific methods within the bot. It's the central hub for processing different types of bot events. Sum it up: defines what your bot does when it receives different types of activities.

    Turn Context: Each handler method receives a TurnContext object. This object provides access to:
    1. The incoming Activity.
    2. The adapter.
    3. State management accessors (ConversationState, UserState).
    4. Methods for sending replies (turn_context.send_activity).

    The Bot's Logic Entry Point: The handler methods are where the bot's high-level logic begins for each turn. This class act as the entry point to interact with the services, repositories, and the Langchain agent.
    """

    def __init__(
        self,
        faq_service: FaqService,
        contact_service: ContactService,
        domain_client_service: DomainClientService,
        reset_password_service: ResetPasswordService,
        db_session: AsyncSession
    ):
        self._faq_service = faq_service
        self._contact_service = contact_service
        self._domain_client_service = domain_client_service
        self._reset_password_service = reset_password_service
        self._db_session = db_session

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Handle incoming messages.
        """
        # Get user data handler for the current turn
        user_data_handler = await self._get_user_data_handler(turn_context)

        email = await user_data_handler.get_email()
        client_type = await user_data_handler.get_client_type()
        user_input = turn_context.activity.text.lower()

        response_text = f"You said: {user_input}"
        if user_input and "contact" in user_input and client_type:
            contacts = await self._contact_service.get_streams(client_type)
            response_text = f"You asked about Contact. here's the result:\n {contacts}"
        elif user_input and "reset password" in user_input and client_type != "UNKNOWN" and email:
            print(
                "--- User input suggests password reset. Calling ResetPasswordService... ---")
            # Pass necessary info to the service method
            await user_data_handler.autogenerate_session_id()
            reset_result = await self._reset_password_service.initiate_sap_password_reset(
                user_email=email,
                session_id=await user_data_handler.get_session_id(),
                client_details=await user_data_handler.get_domain_client_details_model(),
                session=self._db_session
            )
            print(f"--- ResetPasswordService returned: {reset_result} ---")
            response_text = f"Attempted SAP password reset. Result: {reset_result.get('text', 'No text provided')}"
        elif user_input and "key user" in user_input and client_type:
            # For now, just get available streams and ask the user
            get_stream_intent = await self._contact_service.find_stream_from_text(client_type, user_input)
            contacts = await self._contact_service.select_all_by_stream_and_substream(client_type, get_stream_intent)
            if contacts:
                response_text = "\n\n---\n\n".join([
                    f"Name: {contact.contact_name}\n\n"
                    f"Email: {contact.contact_email}\n\n"
                    f"Phone: {contact.contact_phone}\n\n"
                    f"Stream: {contact.stream} / {contact.sub_stream}\n\n"
                    f"Created: {contact.created_date.strftime('%Y-%m-%d') if contact.created_date else 'N/A'}\n\n"
                    f"Updated: {contact.changed_date.strftime('%Y-%m-%d') if contact.changed_date else 'N/A'}\n\n"
                    f"Contact ID: {contact.contact_id}"
                    for contact in contacts
                ])
            else:
                response_text = "Sorry, I don't have Key User information available for your client at the moment."
        await turn_context.send_activity(response_text)

        # --- Later: Integrate Agno agent here ---
        # response = await self._agno_agent.process_input(turn_context, user_data_handler, session_id, self._db_session) # Pass session to agent if needed
        # await turn_context.send_activity(response)

    async def on_members_added_activity(self, members_added: list[ChannelAccount], turn_context: TurnContext):
        """
        Handle when members are added to the conversation.
        Send a welcome message.
        """
        for member in members_added:
            # Check if the added member is the bot itself, turn_context.activity.recipient.id is bot's ID
            if member.id != turn_context.activity.recipient.id:
                # Get user data handler for the current turn
                user_data_handler = await self._get_user_data_handler(turn_context)
                await user_data_handler.set_email_from_activity()
                await user_data_handler.determine_and_set_client_type()
                email = await user_data_handler.get_email()  # Get updated email
                client_type = await user_data_handler.get_client_type()  # Get updated client type

                welcome_message = f"Hello! I'm your bot. How can I help you today?\nNew member Email: {email}\nClient Type: {client_type}"
                await turn_context.send_activity(welcome_message)
                await user_data_handler.set_dialog_welcome_sent(True)

    async def _get_user_data_handler(self, turn_context: TurnContext):
        """
        Helper method to get or create UserDataHandler.
        This will use the user state accessor.
        encapsulate the logic of getting or creating a UserDataHandler instance for the current turn. It acts as a convenient way for handler methods (on_message_activity, on_members_added_activity) to access user-specific data and state in a structured way via the UserDataHandler class.
        """
        user_data_handler = UserDataHandler(
            turn_context,
            domain_client_service=self._domain_client_service
        )
        return user_data_handler
