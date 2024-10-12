from fastapi import FastAPI

from src.routers.articles.views import router as articles_router
from src.routers.auth.views import router as auth_router
from src.routers.sessions.views import router as sessions_router
from src.routers.users.views import router as users_router


app = FastAPI()

app.include_router(articles_router)
app.include_router(auth_router)
app.include_router(sessions_router)
app.include_router(users_router)