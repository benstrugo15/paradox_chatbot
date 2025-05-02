from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.chatbot_service import Chatbot
from services.neural_search_service import NeuralSearcher
from services.conversation_service import ConversationService
from services.request_handler import RequestHandler
from dependencies import get_chatbot, get_neural_searcher, get_conversation_service, get_request_handler

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
    conversation_id, final_message = await request_handler.process_request(
        query.conversation_id, 
        query.message
    )
    
    if not final_message:
        raise HTTPException(status_code=400, detail="No message to process")
    
    await conversation_service.add_message(conversation_id, "user", final_message)
    context_messages = await conversation_service.get_last_messages(conversation_id, 5)
    retrieved_data = neural_searcher.search(text=final_message)
    output = chatbot.search(retrieved_data, final_message, context_messages)
    await conversation_service.add_message(conversation_id, "assistant", output)
    
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
        summary = await conversation_service.get_summary(request.conversation_id)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 