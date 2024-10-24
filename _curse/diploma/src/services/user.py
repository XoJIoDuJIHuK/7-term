import uuid
from typing import Tuple, List

from fastapi import HTTPException, status

from src.database.models import User
from src.pagination import PaginationParams, paginate
from src.routers.users.schemes import CreateUserScheme, FilterUserScheme, \
    UserOutScheme, EditUserScheme

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.util.auth.helpers import get_password_hash
from src.util.time.helpers import get_utc_now


class UserRepository:
    @staticmethod
    async def get_by_id(
            user_id: uuid.UUID,
            db_session: AsyncSession
    ) -> User | None:
        result = await db_session.execute(select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None),
        ))
        return result.scalars().first()

    @staticmethod
    async def get_by_email(
            email: str,
            db_session: AsyncSession
    ) -> User | None:
        result = await db_session.execute(select(User).where(
            User.email == email,
            User.deleted_at.is_(None),
        ))
        return result.scalars().first()

    @staticmethod
    async def get_list(
            pagination_params: PaginationParams,
            filter_params: FilterUserScheme,
            db_session: AsyncSession
    ) -> Tuple[List[UserOutScheme], int]:
        # TODO: implement proper sorting
        query = select(User).where(User.deleted_at.is_(None))
        if filter_params.role is not None:
            query = query.where(User.role == filter_params.role)
        if filter_params.email_verified is not None:
            query = query.where(
                User.email_verified == filter_params.email_verified
            )
        users, count = await paginate(
            session=db_session,
            statement=query,
            pagination=pagination_params
        )
        users_list = [UserOutScheme.model_validate(u) for u in users]
        return users_list, count

    @staticmethod
    async def create(
            user_data: CreateUserScheme,
            db_session: AsyncSession
    ) -> User:
        existing_user = await UserRepository.get_by_email(
            user_data.email,
            db_session
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Адрес электронной почты занят'
            )
        user = User(
            name=user_data.name,
            email=user_data.email,
            email_verified=user_data.email_verified,
            password_hash=get_password_hash(user_data.password),
            role=user_data.role,
            logged_with_provider=user_data.logged_with_provider,
            provider_id=user_data.provider_id
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @staticmethod
    async def update(
            user: User,
            new_data: EditUserScheme,
            db_session: AsyncSession
    ) -> User:
        for key, value in vars(new_data).items():
            if value is not None:
                user.__setattr__(key, value)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @staticmethod
    async def update_password_hash(
            user_id: uuid.UUID,
            new_password_hash: str,
            db_session: AsyncSession
    ) -> int:
        result = await db_session.execute(update(User).where(
            User.id == user_id
        ).values(password_hash=new_password_hash))
        return result.rowcount

    @staticmethod
    async def delete(
            user: User,
            db_session: AsyncSession
    ) -> User:
        user.deleted_at = get_utc_now()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user
