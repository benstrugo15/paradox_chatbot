from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.chatbot_service import Chatbot
from services.neural_search_service import NeuralSearcher
from services.conversation_service import ConversationService
from services.request_handler import RequestHandler
from dependencies import get_chatbot, get_neural_searcher, get_conversation_service, get_request_handler
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["chat"])


class Query(BaseModel):
    message: str
    conversation_id: str = None


class SummarizeRequest(BaseModel):
    conversation_id: str


@router.post("/query")
async def query(
        query: Query,
        chatbot: Chatbot = Depends(get_chatbot),
        neural_searcher: NeuralSearcher = Depends(get_neural_searcher),
        conversation_service: ConversationService = Depends(get_conversation_service),
        request_handler: RequestHandler = Depends(get_request_handler)
):
    conversation_id, message = await request_handler.process_request(
        query.conversation_id,
        query.message
    )
    if not message:
        raise HTTPException(status_code=400, detail="No message to process")
    message_time = datetime.now()
    await conversation_service.add_message(conversation_id, "user", message, message_time)
    context_messages = await conversation_service.get_context_messages(conversation_id, message_time)
    retrieved_data = neural_searcher.search(text=message, context_messages=context_messages)
    output = chatbot.search(retrieved_data, message, context_messages)
    is_last_message = conversation_service.is_last_message(conversation_id, message_time)
    if not is_last_message:
        return {
            "output": "This message is part of a multi-message request."
                      " Please wait for the final message to receive a complete response.",
            "conversation_id": conversation_id
        }
    await conversation_service.add_message(conversation_id, "assistant", output, message_time)
    return {
        "output": output,
        "conversation_id": conversation_id
    }


@router.post("/summarize")
async def summarize(
        request: SummarizeRequest,
        conversation_service: ConversationService = Depends(get_conversation_service)
):
    try:
        summary = await conversation_service.get_summary(request.conversation_id, datetime.now())
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
