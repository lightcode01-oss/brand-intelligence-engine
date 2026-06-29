from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.exceptions.errors import NomenException
from app.core.logging import logger

def register_exception_handlers(app: FastAPI) -> None:
    """Registers unified JSON response format override mappings for all system exceptions."""

    def build_envelope(success: bool, message: str, request: Request, status_code: int, errors: list[str] = None) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "system")
        return JSONResponse(
            status_code=status_code,
            content={
                "success": success,
                "message": message,
                "data": None,
                "meta": {
                    "request_id": request_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "api_version": app.version
                },
                "errors": errors or []
            }
        )

    @app.exception_handler(NomenException)
    async def nomen_exception_handler(request: Request, exc: NomenException) -> JSONResponse:
        logger.warning(f"Domain exception intercepted: {exc.message}", extra={"request_id": getattr(request.state, "request_id", "system")})
        return build_envelope(False, exc.message, request, exc.status_code, exc.errors)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [f"{'.'.join(str(p) for p in err['loc'][1:])}: {err['msg']}" for err in exc.errors()]
        logger.info(f"Input validation error: {errors}", extra={"request_id": getattr(request.state, "request_id", "system")})
        return build_envelope(False, "Input validation failed.", request, 422, errors)

    @app.exception_handler(IntegrityError)
    async def db_integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.error(f"Database Integrity violation: {str(exc.orig)}", exc_info=True, extra={"request_id": getattr(request.state, "request_id", "system")})
        return build_envelope(False, "Database conflict occurred.", request, 409, [str(exc.orig)])

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        logger.info(f"HTTP exception: {exc.detail}", extra={"request_id": getattr(request.state, "request_id", "system")})
        return build_envelope(False, exc.detail, request, exc.status_code)

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unexpected systems failure: {str(exc)}", exc_info=True, extra={"request_id": getattr(request.state, "request_id", "system")})
        return build_envelope(False, "An unexpected system error occurred.", request, 500, [str(exc)])
