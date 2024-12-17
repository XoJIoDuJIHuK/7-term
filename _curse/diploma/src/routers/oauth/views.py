from src.depends import get_session

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Request,
)
from fastapi.responses import RedirectResponse

from src.database.repos.user import UserRepo
from src.logger import get_logger
from src.settings import OAuthConfig, OAuthProvider, Role

from sqlalchemy.ext.asyncio import AsyncSession

from src.util.auth.classes import AuthHandler
from src.util.auth.helpers import get_authenticated_response
from src.util.oauth.helpers import get_oauth_provider
from src.util.storage.classes import RedisHandler


router = APIRouter(
    prefix='/oauth',
    tags=['OAuth'],
)
logger = get_logger(__name__)


@router.get(
    '/login/'
)
async def redirect_to_provider(
        request: Request,
        provider: OAuthProvider,
):
    provider_authorize = get_oauth_provider(
        provider=provider,
        storage=RedisHandler()
    )
    new_session_data = {
        OAuthConfig.session_data_property: {
            'ip': request.client.host,
        }
    }
    request.session.update(new_session_data)
    authorization_url = await provider_authorize.get_auth_url()
    return RedirectResponse(authorization_url)


@router.get(
    '/{provider}/callback',
    summary='Validates auth code from provider and returns user\'s tokens',
    response_model=None
)
async def callback(
    request: Request,
    provider: OAuthProvider = Path(),
    db_session: AsyncSession = Depends(get_session),
):
    oauth_login_data = request.session.get(
        OAuthConfig.session_data_property
    )
    if not oauth_login_data:
        error_message = (
            f'Ошибка валидации сессии: {request.session}, отсутствует свойство'
            f' \'{OAuthConfig.session_data_property}\''
        )
        logger.error(error_message)
        raise Exception(error_message)

    provider_authorize = get_oauth_provider(
        provider=provider,
        storage=RedisHandler()
    )
    auth_token = await provider_authorize.callback(
        request=request
    )

    user_data = await provider_authorize.get_user_info(auth_token)
    logger.error(user_data)
    user_id = user_data.id
    provider_user_id = (str(user_id) if user_id else None)

    if email := user_data.email:
        user = await UserRepo.get_by_email(
            email=email,
            db_session=db_session
        )
        if not user:
            user = await UserRepo.register_for_oauth(
                role=Role.user,
                db_session=db_session,
                email=email,
                name=user_data.name,
                oauth_provider=provider,
                provider_id=provider_user_id,
            )
    else:
        user = await UserRepo.get_by_oauth_data(
            provider=provider,
            provider_id=provider_user_id,
            db_session=db_session
        )
        if not user:
            user = await UserRepo.register_for_oauth(
                email=None,
                name=user_data.name,
                role=Role.user,
                db_session=db_session,
                oauth_provider=provider,
                provider_id=provider_user_id,
            )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    tokens = await AuthHandler.login(
        user=user,
        request=request,
        db_session=db_session
    )
    return get_authenticated_response(tokens)
