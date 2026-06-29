from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# Core and Middleware imports
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.docs import setup_docs_overrides
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.timing import TimingMiddleware
from app.middleware.security import SecurityHeadersMiddleware, MaintenanceModeMiddleware
from app.exceptions.handlers import register_exception_handlers

# Versioned router namespaces
from app.api.v1 import router as v1_router

def create_app() -> FastAPI:
    """Application factory initializing system logger, middlewares, exception rules, and routers."""
    # 1. Setup structured logging
    setup_logging()
    
    # 2. Instantiate FastAPI
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url=None,   # Disable default docs to support custom overrides
        redoc_url=None,  # Disable default redoc
        terms_of_service="https://nomen.ai/terms",
        contact={
            "name": "Nomen Engineering Support",
            "url": "https://nomen.ai/support",
            "email": "support@nomen.ai",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        }
    )
    
    # 3. Register standard Middlewares
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Register custom pipeline middlewares
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(MaintenanceModeMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    
    # 4. Register Exception Handlers
    register_exception_handlers(app)
    
    # 5. Wire Custom Documentation Paths
    setup_docs_overrides(app)
    
    # 6. Mount Versioned Routers (supports v1, v2 side-by-side)
    app.include_router(v1_router, prefix=f"{settings.API_PREFIX}/v1")
    
    return app

# Instantiate global app target for server entry run
app = create_app()
