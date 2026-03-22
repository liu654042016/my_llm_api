import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import load_config
from src.core.router import Router
from src.core.health import HealthChecker
from src.api.routes import router as api_router, set_router, set_health_checker


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources."""
    # Load config
    config = load_config("config.yaml")
    
    # Initialize router and health checker
    router = Router(config)
    health_checker = HealthChecker(config)
    
    set_router(router)
    set_health_checker(health_checker)
    
    logger.info(f"Initialized with {len(config.adapters)} adapters")
    
    yield
    
    # Cleanup
    await router.close()
    await health_checker.close()
    logger.info("Shutdown complete")


app = FastAPI(
    title="LLM API Proxy",
    description="Minimal LLM API proxy with OpenAI-compatible interface",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router)
