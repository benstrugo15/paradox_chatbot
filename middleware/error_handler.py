from fastapi import Request, status
from fastapi.responses import JSONResponse
from exceptions import ChatbotException
import logging
import traceback
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)


async def error_handler_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[JSONResponse]]
) -> JSONResponse:
    try:
        return await call_next(request)
    except ChatbotException as e:
        logger.error(f"Chatbot error: {str(e)}")
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.message}
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "An unexpected error occurred"}
        )
