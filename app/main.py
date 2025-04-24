from fastapi import FastAPI

# from app.modules.auth.routes import router as auth_router
from app.modules.voting.routes import router as voting_router
from app.modules.admin.routes import router as admin_router

app = FastAPI()

# app.include_router(auth_router)
app.include_router(voting_router)
app.include_router(admin_router)

@app.get("/")
def read_root():
    return {"message": "Hello, SQR Voting System!"}