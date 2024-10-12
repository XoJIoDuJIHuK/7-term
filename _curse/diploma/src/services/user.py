import uuid

from fastapi import HTTPException, status

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate

from src.database import get_session
from src.database.models import User
from src.routers.users.schemes import CreateUserScheme, FilterUserScheme

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    @staticmethod
    async def get_by_id(
            user_id: uuid.UUID,
            db_session: AsyncSession
    ) -> User | None:
        result = await db_session.execute(select(User).where(
            User.id == user_id
        ))
        return result.scalars().first()

    @staticmethod
    async def get_by_email(
            email: str,
            db_session: AsyncSession
    ) -> User | None:
        result = await db_session.execute(select(User).where(
            User.email == email
        ))
        return result.scalars().first()

    @staticmethod
    async def get_list(
            pagination_params: Params,
            filter_params: FilterUserScheme,
            db_session: AsyncSession
    ) -> Page[User]:
        # TODO: implement proper sorting
        query = select(User)
        if filter_params.role is not None:
            query = query.where(User.role == filter_params.role)
        if filter_params.email_verified is not None:
            query = query.where(
                User.email_verified == filter_params.email_verified
            )
        return await paginate(
            conn=db_session,
            query=query,
            params=pagination_params
        )

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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Адрес электронной почты занят'
            )
        user = User(
            name=user_data.name,
            email=user_data.email,
            email_verified=user_data.email_verified,
            password_hash=user_data.password_hash,
            role=user_data.role,
            logged_wiht_provider=user_data.logged_with_provider,
            provider_id=user_data.provider_id
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user
