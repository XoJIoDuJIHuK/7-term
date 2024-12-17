import uuid
from typing import Tuple, List

from fastapi import HTTPException, status

from src.database.models import User
from src.pagination import PaginationParams, paginate
from src.routers.users.schemes import CreateUserScheme, FilterUserScheme, \
    UserOutScheme, EditUserScheme

from sqlalchemy import delete, exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.settings import OAuthProvider, Role
from src.util.auth.helpers import get_password_hash
from src.util.time.helpers import get_utc_now


class UserRepo:
    @staticmethod
    async def name_is_taken(
            name: str,
            db_session: AsyncSession
    ) -> bool:
        result = await db_session.execute(select(exists().where(
            User.name == name
        )))
        return result.scalar_one()

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
    async def register_for_oauth(
            role: Role,
            db_session: AsyncSession,
            oauth_provider: OAuthProvider,
            name: str,
            email: str | None,
            password_hash: str = '',
            provider_id: str | None = None,
    ) -> User:
        user = User(
            email=email,
            name=name,
            password_hash=password_hash,
            role=role,
            logged_with_provider=oauth_provider,
            provider_id=provider_id,
        )
        if email:
            user.email_verified = True
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @staticmethod
    async def get_by_oauth_data(
            provider: OAuthProvider,
            provider_id: str,
            db_session: AsyncSession
    ) -> User | None:
        """
        Returns user by provider name and user's id of given provider
        """
        query = (select(User).filter_by(
            logged_with_provider=provider,
            provider_id=provider_id
        ))
        result = await db_session.execute(query)
        user = result.scalar()
        return user

    @staticmethod
    async def create(
            user_data: CreateUserScheme,
            db_session: AsyncSession
    ) -> User:
        existing_user = await UserRepo.get_by_email(
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
        for key, value in filter(
            lambda x: x != 'password',
            vars(new_data).items()
        ):
            if value is not None:
                user.__setattr__(key, value)
        if new_data.password:
            user.password_hash = get_password_hash(new_data.password)
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
        await db_session.commit()
        return result.rowcount

    @classmethod
    async def soft_delete(
            cls,
            user: User,
            db_session: AsyncSession
    ) -> User:
        new_email = '@' + user.email
        try:
            await cls.hard_delete(new_email, db_session)
        except HTTPException:
            pass
        user.email = new_email
        user.deleted_at = get_utc_now()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @staticmethod
    async def hard_delete(
            email: str,
            db_session: AsyncSession
    ):
        result = await db_session.execute(delete(User).where(
            User.email == email
        ))
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Удаление невозможно: пользователь не найден'
            )
        await db_session.commit()
