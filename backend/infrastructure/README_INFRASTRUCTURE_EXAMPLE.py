"""
Infrastructure layer - Implementation details

This layer:
- Implements repository interfaces
- Implements service interfaces
- Handles database access
- Handles external APIs
- Can depend on anything
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.README_DOMAIN_EXAMPLE import (
    User as DomainUser,
    Tenant as DomainTenant,
    Email, TenantSlug,
    IUserRepository, ITenantRepository
)

# SQLAlchemy Models (Persistence layer)
from app.models.user import User as UserModel
from app.models.tenant import Tenant as TenantModel


# Repository Implementations
class UserRepository(IUserRepository):
    """
    User repository implementation using SQLAlchemy

    Benefits:
    - Easy to test (can mock)
    - Easy to switch database
    - Encapsulates query logic
    - Domain layer doesn't know about SQLAlchemy
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, user_id: int) -> Optional[DomainUser]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_username(self, username: str) -> Optional[DomainUser]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_email(self, email: Email) -> Optional[DomainUser]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email.value)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def save(self, user: DomainUser) -> DomainUser:
        if user.id is None:
            # Create new
            model = UserModel(
                username=user.username,
                email=user.email.value,
                hashed_password=user.hashed_password,
                is_active=user.is_active(),
                is_admin=user.is_admin()
            )
            self.session.add(model)
            await self.session.flush()
            user.id = model.id
        else:
            # Update existing
            model = await self.session.get(UserModel, user.id)
            model.username = user.username
            model.email = user.email.value
            model.is_active = user.is_active()
            model.is_admin = user.is_admin()

        return user

    async def delete(self, user_id: int) -> bool:
        model = await self.session.get(UserModel, user_id)
        if model:
            await self.session.delete(model)
            return True
        return False

    def _to_domain(self, model: UserModel) -> DomainUser:
        """Convert SQLAlchemy model to domain entity"""
        return DomainUser(
            id=model.id,
            username=model.username,
            email=Email(model.email),
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            is_admin=model.is_admin
        )


class TenantRepository(ITenantRepository):
    """Tenant repository implementation"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, tenant_id: int) -> Optional[DomainTenant]:
        model = await self.session.get(TenantModel, tenant_id)
        return self._to_domain(model) if model else None

    async def find_by_slug(self, slug: TenantSlug) -> Optional[DomainTenant]:
        result = await self.session.execute(
            select(TenantModel).where(TenantModel.slug == slug.value)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[DomainTenant]:
        result = await self.session.execute(
            select(TenantModel).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def save(self, tenant: DomainTenant) -> DomainTenant:
        if tenant.id is None:
            model = TenantModel(
                name=tenant.name,
                slug=tenant.slug.value,
                schema_name=tenant.get_schema_name(),
                admin_email=tenant.admin_email.value,
                is_active=tenant.is_active()
            )
            self.session.add(model)
            await self.session.flush()
            tenant.id = model.id
        else:
            model = await self.session.get(TenantModel, tenant.id)
            model.name = tenant.name
            model.is_active = tenant.is_active()

        return tenant

    async def delete(self, tenant_id: int) -> bool:
        model = await self.session.get(TenantModel, tenant_id)
        if model:
            await self.session.delete(model)
            return True
        return False

    def _to_domain(self, model: TenantModel) -> DomainTenant:
        """Convert SQLAlchemy model to domain entity"""
        return DomainTenant(
            id=model.id,
            name=model.name,
            slug=TenantSlug(model.slug),
            admin_email=Email(model.admin_email),
            is_active=model.is_active,
            is_trial=model.is_trial
        )


# Service Implementations
class PasswordService:
    """Password hashing service implementation"""

    def __init__(self):
        from passlib.context import CryptContext
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        return self.pwd_context.verify(password, hashed)


class TokenService:
    """JWT token service implementation"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(self, data: dict) -> str:
        from jose import jwt
        from datetime import datetime, timedelta

        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict:
        from jose import jwt, JWTError

        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            raise InvalidTokenException()


# Unit of Work Implementation
class SqlAlchemyUnitOfWork:
    """
    Unit of Work pattern implementation

    Benefits:
    - Transaction management
    - Atomic operations
    - Rollback on error
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
