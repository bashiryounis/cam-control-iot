import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from src.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI(
    debug=True,
    title="Camera Control API",
    description="translates complex camera commands into a simple, unified API, enabling seamless control of diverse cameras directly from your web dashboard",
)

# Enable CORS for all origins (adjust as necessary for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Redirect root URL to the API documentation
@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs/")