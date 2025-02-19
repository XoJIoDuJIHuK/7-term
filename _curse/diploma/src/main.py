from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.handlers import (
    init_exc_handlers,
    init_responses,
)

from src.settings import AppConfig

from src.routers.articles.views import router as articles_router
from src.routers.analytics.views import router as analytics_router
from src.routers.auth.views import router as auth_router
from src.routers.reports.views import router as reports_router
from src.routers.config.views import router as config_router
from src.routers.languages.views import router as languages_router
from src.routers.models.views import router as models_router
from src.routers.notifications.views import router as notifications_router
from src.routers.oauth.views import router as oauth_router
from src.routers.prompts.views import router as prompts_router
from src.routers.sessions.views import router as sessions_router
from src.routers.translation.views import router as translation_router
from src.routers.users.views import router as users_router

from starlette.middleware.cors import CORSMiddleware


app = FastAPI(root_path='/api')
app_config = AppConfig()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.add_middleware(SessionMiddleware, secret_key=app_config.secret_key)

init_exc_handlers(app, app_config.debug)
init_responses(app)

app.include_router(articles_router)
app.include_router(analytics_router)
app.include_router(auth_router)
app.include_router(config_router)
app.include_router(languages_router)
app.include_router(models_router)
app.include_router(notifications_router)
app.include_router(oauth_router)
app.include_router(prompts_router)
app.include_router(reports_router)
app.include_router(sessions_router)
app.include_router(users_router)
app.include_router(translation_router)


@app.post('/test/')
async def post_test_message():
    from src.util.brokers.producer.rabbitmq import publish_message

    publish_message('lmao', '{"xd": "omegalul"}')
