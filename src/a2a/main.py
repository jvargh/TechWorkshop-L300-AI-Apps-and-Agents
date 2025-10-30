import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor

from a2a.api.chat import router as chat_router
from a2a.agent.a2a_server import A2AServer

# Load environment variables early
load_dotenv()

# Configure Azure Monitor for observability
try:
    application_insights_connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if application_insights_connection_string:
        configure_azure_monitor(connection_string=application_insights_connection_string)
        logging.info("Azure Monitor observability configured successfully")
    else:
        logging.warning("APPLICATIONINSIGHTS_CONNECTION_STRING not found - Azure Monitor not configured")
except Exception as e:
    logging.error(f"Failed to configure Azure Monitor: {e}")

# Configure OpenAI instrumentation for AI model request tracing
try:
    OpenAIInstrumentor().instrument()
    logging.info("OpenAI instrumentation configured successfully")
except Exception as e:
    logging.error(f"Failed to configure OpenAI instrumentation: {e}")

# Initialize OpenTelemetry tracer
tracer = trace.get_tracer(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for telemetry attributes
HTTP_METHOD_ATTR = "http.method"
HTTP_ROUTE_ATTR = "http.route"

# Global variables for cleanup
httpx_client: httpx.AsyncClient = None
a2a_server: A2AServer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global httpx_client, a2a_server
    
    # Startup
    with tracer.start_as_current_span("a2a_application_startup") as startup_span:
        logger.info("Starting Zava Product Manager with A2A integration...")
        startup_span.set_attribute("service.name", "zava-product-manager")
        startup_span.set_attribute("service.version", "1.0.0")
        
        httpx_client = httpx.AsyncClient(timeout=30)
        
        # Initialize A2A server
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8001))
        
        startup_span.set_attribute("server.host", host)
        startup_span.set_attribute("server.port", port)
        
        a2a_server = A2AServer(httpx_client, host=host, port=port)
        
        # Mount A2A endpoints to the main app
        app.mount("/a2a", a2a_server.get_starlette_app(), name="a2a")
        
        logger.info(
            f"A2A server mounted at / - Agent Card available at "
            f"http://{host}:{port}/agent-card/"
        )
        startup_span.set_attribute("startup.status", "success")
    
    yield
    
    # Shutdown
    with tracer.start_as_current_span("a2a_application_shutdown") as shutdown_span:
        logger.info("Shutting down Zava Product Manager...")
        if httpx_client:
            await httpx_client.aclose()
        shutdown_span.set_attribute("shutdown.status", "success")


# Create FastAPI app
app = FastAPI(
    title="Zava Product Manager",
    description=(
        "A standalone web application for Zava Product Manager"
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Setup templates
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=templates_path)

# Include API routes
app.include_router(chat_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main chat interface"""
    with tracer.start_as_current_span("serve_chat_interface") as span:
        span.set_attribute(HTTP_METHOD_ATTR, "GET")
        span.set_attribute(HTTP_ROUTE_ATTR, "/")
        return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint for Azure App Service"""
    with tracer.start_as_current_span("health_check") as span:
        span.set_attribute(HTTP_METHOD_ATTR, "GET")
        span.set_attribute(HTTP_ROUTE_ATTR, "/health")
        result = {"status": "healthy", "service": "zava-product-manager"}
        span.set_attribute("health.status", result["status"])
        return result


@app.get("/agent-card")
async def get_agent_card():
    """Expose the A2A Agent Card for discovery"""
    with tracer.start_as_current_span("get_agent_card") as span:
        span.set_attribute(HTTP_METHOD_ATTR, "GET")
        span.set_attribute(HTTP_ROUTE_ATTR, "/agent-card")
        if a2a_server:
            result = a2a_server._get_agent_card()
            span.set_attribute("agent_card.available", True)
            return result
        span.set_attribute("agent_card.available", False)
        return {"error": "A2A server not initialized"}


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8001))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(app, host=host, port=port, reload=debug)
