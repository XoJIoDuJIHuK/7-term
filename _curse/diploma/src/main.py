from fastapi import FastAPI

from src.handlers import (
    init_exc_handlers,
    init_responses,
)

from src.settings import AppConfig

from src.routers.articles.views import router as articles_router
from src.routers.auth.views import router as auth_router
from src.routers.config.views import router as config_router
from src.routers.languages.views import router as languages_router
from src.routers.models.views import router as models_router
from src.routers.reports.views import router as reports_router
from src.routers.sessions.views import router as sessions_router
from src.routers.translation.views import router as translation_router
from src.routers.users.views import router as users_router

from starlette.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_exc_handlers(app, AppConfig.debug)
init_responses(app)

app.include_router(articles_router)
app.include_router(auth_router)
app.include_router(config_router)
app.include_router(languages_router)
app.include_router(models_router)
app.include_router(reports_router)
app.include_router(sessions_router)
app.include_router(users_router)
app.include_router(translation_router)
