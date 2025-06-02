from pydantic import BaseModel
from typing import Dict, Any, List


class UserData(BaseModel):  # Define the structure for the user's data stored in state
    """
    Represents the user-specific data stored in the bot's user state.
    """
    # Basic info derived from the Teams activity
    email: str | None = None
    client_type: str | None = None  # e.g., "ACCENTURE", "AMMAN"
    # Store details from domain lookup
    domain_client_details: Dict[str, Any] | None = None
    session_id: str | None = None

    # State for conversational flow (e.g., dialog tracking, if not using dialog stack)
    # You might simplify this if Langchain agent manages most flow
    # current_dialog_id: Optional[str] = None
    # dialog_state: Optional[Dict[str, Any]] = None

    # State related to specific features
    current_faq_question: str | None = None
    # Store potential FAQ results
    current_faq_suggestions: List[Dict[str, Any]] | None = None
    selected_faq_index: int | None = None  # Store the index of the selected FAQ

    # State related to Reset Password
    reset_password_confirmed: bool | None = None
    reset_password_session_id: str | None = None  # Store the session ID for logging

    # Language preference
    language: str = "ID"  # Default language

    # Welcome message tracking
    dialog_welcome_sent: bool = False

    # Add any other user-specific state data you need
    # For example:
    # last_interaction_time: Optional[datetime] = None
    # referral_id: Optional[str] = None
