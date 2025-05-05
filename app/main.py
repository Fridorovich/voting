from fastapi import FastAPI, Request
import logging
from app.modules.auth.routes import router as auth_router
from app.modules.voting.routes import router as voting_router
from app.modules.admin.routes import router as admin_router
from app.shared.logging import setup_logging

setup_logging()

app = FastAPI()

app.include_router(auth_router)
app.include_router(voting_router)
app.include_router(admin_router)

@app.get("/")
def read_root():
    return {"message": "Hello, SQR Voting System!"}

@app.middleware("http")
async def skip_auth_for_docs(request: Request, call_next):
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    response = await call_next(request)
    return response

logger = logging.getLogger(__name__)

@app.get("/test_log")
def test_log():
    logger.info("Test log message triggered!")
    return {"message": "Log written!"}