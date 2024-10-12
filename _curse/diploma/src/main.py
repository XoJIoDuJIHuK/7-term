from fastapi import FastAPI

from src.routers.auth.views import router as auth_router
from src.routers.sessions.views import router as sessions_router


app = FastAPI()

app.include_router(auth_router)
app.include_router(sessions_router)