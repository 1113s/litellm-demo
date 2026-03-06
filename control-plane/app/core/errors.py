from fastapi import Request
from fastapi.responses import JSONResponse


def error_payload(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


async def http_exception_handler(_: Request, exc) -> JSONResponse:
    code = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", "unexpected error")
    message = detail if isinstance(detail, str) else "request failed"
    return JSONResponse(status_code=code, content=error_payload("HTTP_ERROR", message))


async def unhandled_exception_handler(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content=error_payload("INTERNAL_ERROR", "internal server error"))
