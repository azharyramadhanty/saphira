from fastapi import APIRouter, Request, Depends, status, Response
from botbuilder.core import BotFrameworkAdapter
from botbuilder.schema import Activity
from src.dependencies import get_bot_adapter, get_saphira_activity_handler
from src.bots.saphira_activity_handler import SaphiraActivityHandler
import traceback

router = APIRouter()


@router.post("/messages")
async def messages(
    request: Request,
    adapter: BotFrameworkAdapter = Depends(get_bot_adapter),
    activity_handler: SaphiraActivityHandler = Depends(
        get_saphira_activity_handler)
):
    """
    Main endpoint for receiving messages from the Bot Framework Service.
    Process the activity using the adapter, pass the raw activity JSON body and the entry point to bot handler's logic
    The adapter will:
    1. deserializes the body into a Bot Framework Activity object.
    2. It creates a TurnContext object, populating it with the adapter, the activity, and access to the state accessors.
    3. It calls the on_turn method of the ActivityHandler, passing the TurnContext.
    4. The on_turn method then routes the activity to the saphira handler methods implemented (like on_message_activity, on_members_added_activity, etc.)
    """
    if request.headers.get("content-type") == "application/json":
        try:
            body = await request.json()
            body_deserialize = Activity().deserialize(body)
            auth_header = request.headers.get("Authorization")
            await adapter.process_activity(body_deserialize, auth_header, activity_handler.on_turn)
            print("adapter.process_activity completed.")
        except Exception as e:
            print(f"Exception Details: {e}")
            traceback.print_exc()
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
