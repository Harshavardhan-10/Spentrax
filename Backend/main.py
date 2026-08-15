"""Smart Expense & Budget Manager - FastAPI application entry point.

Wires together configuration, logging, CORS, routers and centralized error
handling. Run with:  uvicorn main:app --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api import (
    ai_router,
    analytics_router,
    auth_router,
    budgets_router,
    categories_router,
    csv_router,
    dashboard_router,
    expenses_router,
    recurring_router,
    users_router,
)
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.exceptions import AppError, ErrorCode
from app.core.logging import setup_logging
from app.services.category_service import seed_default_categories
from app.utils.response import error_response

settings = get_settings()
setup_logging(debug=settings.DEBUG)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(_: FastAPI):
    db = SessionLocal()
    try:
        seed_default_categories(db)
        logger.info("Default categories seeded.")
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "REST API for the Smart Expense & Budget Manager: authentication, "
        "expenses, categories, budgets, recurring detection, analytics, "
        "dashboard, CSV import/export and AI-powered insights."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    response = await call_next(request)
    logger.info(
        "%s %s -> %s", request.method, request.url.path, response.status_code
    )
    return response


for api_router in [
    auth_router,
    users_router,
    categories_router,
    expenses_router,
    budgets_router,
    recurring_router,
    analytics_router,
    dashboard_router,
    csv_router,
    ai_router,
]:
    app.include_router(api_router)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.message, exc.error_code.value),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError):
    errors = exc.errors()
    first = errors[0] if errors else {}
    location = ".".join(str(part) for part in first.get("loc", []) if part != "body")
    message = f"{location}: {first.get('msg', 'invalid value')}" if location else "Invalid request data."
    return JSONResponse(
        status_code=422,
        content=error_response(message, ErrorCode.VALIDATION_ERROR.value),
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(_: Request, exc: IntegrityError):
    logger.warning("Integrity error: %s", exc.orig)
    return JSONResponse(
        status_code=409,
        content=error_response(
            "The request conflicts with existing data (e.g. a duplicate record).",
            ErrorCode.VALIDATION_ERROR.value,
        ),
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(_: Request, exc: SQLAlchemyError):
    logger.error("Database error: %s", exc)
    return JSONResponse(
        status_code=500,
        content=error_response(
            "An internal database error occurred. Please try again later.",
            ErrorCode.INTERNAL_ERROR.value,
        ),
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(_: Request, exc: Exception):
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content=error_response(
            "An unexpected error occurred. Please try again later.",
            ErrorCode.INTERNAL_ERROR.value,
        ),
    )


@app.get("/")
def home():
    return {"message": f"{settings.APP_NAME} API is running."}


@app.get("/health")
def health():
    return {"status": "ok", "version": settings.APP_VERSION}
