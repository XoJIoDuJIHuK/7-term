from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from src.settings import Role
from src.util.auth.classes import JWTCookie
from src.util.auth.schemes import UserInfo

router = APIRouter(
    prefix='/analytics',
    tags=['Analytics']
)


@router.get(
    '/'
)
async def get_analytics(
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin]))
):
    # for every model or prompt grouping by every reason (?) and status
    pass