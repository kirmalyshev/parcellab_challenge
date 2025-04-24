import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from src.api.routes import shipments
from src.config.logging import setup_logging


# Setup logging
logger = setup_logging()
logger.info("Starting application...")

API_VERSION = os.getenv("API_VERSION", "0.0.1")

app = FastAPI(
    title="Parcellab Track and Trace API",
    description="API for tracking shipments and getting weather information",
    version=API_VERSION,
    debug=True,  # Enable debug mode
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO replace with specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(shipments.router, prefix="/api/v1", tags=["shipments"])


@app.get("/")
async def root():
    logger.debug("Root endpoint accessed")
    return {"message": "Welcome to Parcellab Track and Trace API"}


@app.get("/swagger", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Parcellab API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Parcellab Track and Trace API",
        version=API_VERSION,
        description="API for tracking shipments and getting weather information",
        routes=app.routes,
    )

    # Customize the OpenAPI schema if needed
    openapi_schema["info"]["x-logo"] = {"url": "https://parcellab.com/wp-content/uploads/2020/10/parcellab-logo.svg"}

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug", reload=True)
