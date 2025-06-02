from botbuilder.core import ConversationState, UserState, StatePropertyAccessor, TurnContext, MemoryStorage, Middleware
from botbuilder.azure import BlobStorage, BlobStorageSettings
from src.config import app_config

"""
State management in the Bot Framework is how bot remembers information about the conversation and the user across multiple turns (messages). Since each incoming message is a separate HTTP request, the bot is essentially stateless by default. State management provides a way to store and retrieve data associated with a specific conversation or user ID.

This file centralizes the setup of these state management components. Create instances of MemoryStorage, ConversationState, and UserState, and define the accessors that will be use throughout the bot and sets up the definitions of how state will be managed.
"""
# Define state property names
CONVERSATION_DATA_PROPERTY = "conversationData"
USER_DATA_PROPERTY = "userData"

# The underlying mechanism for storing the state data.
# Create a MemoryStorage instance (for local development) - Stores state in memory (suitable for local dev, state is lost on restart).
# For production, replace with BlobStorage (Stores state in Azure Blob Storage (persistent)) or CosmosDbStorage (Stores state in Azure Cosmos DB (persistent))
STORAGE: BlobStorage = None

# Create ConversationState and UserState instances
# Tracks state specific to a particular conversation (channel + user). This is used to store information relevant to the current interaction flow, like the state of a dialog.
CONVERSATION_STATE: ConversationState = None
# Tracks state specific to a particular user across all conversations they have with the bot. This is used to store user-specific information, like their client type or email.
USER_STATE: UserState = None

# Create state property accessors
# Provides a convenient way to get, set, and delete specific properties within the conversation or user state objects
CONVERSATION_DATA_ACCESSOR: StatePropertyAccessor = None
USER_DATA_ACCESSOR: StatePropertyAccessor = None

# --- Dependency functions for state accessors (Optional but recommended for DI) ---
# Define dependency keys
CONVERSATION_STATE_KEY = "ConversationState"
USER_STATE_KEY = "UserState"
CONVERSATION_DATA_ACCESSOR_KEY = "ConversationDataAccessor"
USER_STATE_ACCESSOR_KEY = "UserDataAccessor"


async def initialize_state_management():
    """
    Initializes the state storage, state objects, and accessors
    using configuration loaded during lifespan.
    """
    global STORAGE, CONVERSATION_STATE, USER_STATE, CONVERSATION_DATA_ACCESSOR, USER_DATA_ACCESSOR  # Use global

    # Ensure config attributes are populated
    if not all([app_config.AZURE_STORAGE_CONNECTION_STRING, app_config.AZURE_STORAGE_CONTAINER_NAME]):
        print("CRITICAL ERROR: Blob Storage configuration not loaded. Cannot initialize state management.")
        # Decide how to handle failure - maybe raise an error or exit
        raise ValueError("Blob Storage configuration is missing.")

    print("Initializing Blob Storage...")
    # Create BlobStorage instance using loaded config
    blob_settings = BlobStorageSettings(
        container_name=app_config.AZURE_STORAGE_CONTAINER_NAME,
        connection_string=app_config.AZURE_STORAGE_CONNECTION_STRING
    )
    STORAGE = BlobStorage(blob_settings)
    print("Blob Storage initialized.")

    print("Initializing state objects...")
    # Create ConversationState and UserState instances
    CONVERSATION_STATE = ConversationState(STORAGE)
    USER_STATE = UserState(STORAGE)
    print("Conversation and User State initialized.")

    print("Creating state property accessors...")
    # Create state property accessors
    CONVERSATION_DATA_ACCESSOR = CONVERSATION_STATE.create_property(
        CONVERSATION_DATA_PROPERTY)
    USER_DATA_ACCESSOR = USER_STATE.create_property(USER_DATA_PROPERTY)
    print("State property accessors created.")


async def close_state_management():
    """Placeholder for any state storage cleanup."""
    print("Closing state management (Blob Storage has no explicit dispose).")
    # BlobStorage itself often doesn't have a specific dispose method
    # The underlying SDK client might need disposal if managed manually,
    # but botbuilder-azure likely handles this.

# --- Dependency functions for state accessors (Used by other modules) ---
# These functions will return the initialized global instances


def get_conversation_state() -> ConversationState:
    if CONVERSATION_STATE is None:
        raise RuntimeError(
            "ConversationState not initialized. Call initialize_state_management first.")
    return CONVERSATION_STATE


def get_user_state() -> UserState:
    if USER_STATE is None:
        raise RuntimeError(
            "UserState not initialized. Call initialize_state_management first.")
    return USER_STATE


def get_conversation_data_accessor() -> StatePropertyAccessor:
    if CONVERSATION_DATA_ACCESSOR is None:
        raise RuntimeError(
            "Conversation Data Accessor not initialized. Call initialize_state_management first.")
    return CONVERSATION_DATA_ACCESSOR


def get_user_data_accessor() -> StatePropertyAccessor:
    if USER_DATA_ACCESSOR is None:
        raise RuntimeError(
            "User Data Accessor not initialized. Call initialize_state_management first.")
    return USER_DATA_ACCESSOR


"""
# Middleware to make state accessors available in TurnContext state
# This is a common pattern when accessors are managed globally or via dependencies
# The adapter's middleware pipeline is a good place to add this
# You'll need to add this middleware to your BotFrameworkAdapter instance in dependencies.py
"""


class StateAccessorMiddleware(Middleware):
    async def on_turn(self, context: TurnContext, next_logic):
        # Ensure accessors are initialized before accessing
        if CONVERSATION_DATA_ACCESSOR is None or USER_DATA_ACCESSOR is None:
            raise RuntimeError(
                "State Accessors not initialized. Call initialize_state_management first.")
        context.turn_state[CONVERSATION_DATA_ACCESSOR_KEY] = CONVERSATION_DATA_ACCESSOR
        context.turn_state[USER_STATE_ACCESSOR_KEY] = USER_DATA_ACCESSOR
        await next_logic()  # Continue the middleware pipeline
