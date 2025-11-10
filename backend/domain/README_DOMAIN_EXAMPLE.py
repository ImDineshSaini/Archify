"""
Domain layer - Pure business logic, no external dependencies

This layer should NOT depend on:
- FastAPI
- SQLAlchemy
- External libraries

It should only contain pure Python and business rules.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime


# Value Objects (Immutable)
@dataclass(frozen=True)
class Email:
    """Email value object with validation"""
    value: str

    def __post_init__(self):
        if '@' not in self.value:
            raise ValueError("Invalid email format")


@dataclass(frozen=True)
class TenantSlug:
    """Tenant slug value object"""
    value: str

    def __post_init__(self):
        if not self.value.islower() or not self.value.replace('-', '').isalnum():
            raise ValueError("Slug must be lowercase alphanumeric with hyphens")


# Domain Entities
class User:
    """User domain entity - Pure business logic"""

    def __init__(
        self,
        id: Optional[int],
        username: str,
        email: Email,
        hashed_password: str,
        is_active: bool = True,
        is_admin: bool = False
    ):
        self.id = id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self._is_active = is_active
        self._is_admin = is_admin

    def activate(self):
        """Activate user account"""
        self._is_active = True

    def deactivate(self):
        """Deactivate user account"""
        self._is_active = False

    def make_admin(self):
        """Grant admin privileges"""
        self._is_admin = True

    def is_active(self) -> bool:
        return self._is_active

    def is_admin(self) -> bool:
        return self._is_admin

    def can_login(self) -> bool:
        """Business rule: User can login if active"""
        return self._is_active


class Tenant:
    """Tenant domain entity"""

    def __init__(
        self,
        id: Optional[int],
        name: str,
        slug: TenantSlug,
        admin_email: Email,
        is_active: bool = True,
        is_trial: bool = True
    ):
        self.id = id
        self.name = name
        self.slug = slug
        self.admin_email = admin_email
        self._is_active = is_active
        self._is_trial = is_trial

    def get_schema_name(self) -> str:
        """Business rule: Schema name is always tenant_{slug}"""
        return f"tenant_{self.slug.value}"

    def activate(self):
        self._is_active = True

    def deactivate(self):
        self._is_active = False

    def convert_to_paid(self):
        """Convert from trial to paid"""
        self._is_trial = False

    def is_active(self) -> bool:
        return self._is_active


# Repository Interfaces (Ports)
class IUserRepository(ABC):
    """User repository interface"""

    @abstractmethod
    async def find_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        pass


class ITenantRepository(ABC):
    """Tenant repository interface"""

    @abstractmethod
    async def find_by_id(self, tenant_id: int) -> Optional[Tenant]:
        pass

    @abstractmethod
    async def find_by_slug(self, slug: TenantSlug) -> Optional[Tenant]:
        pass

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Tenant]:
        pass

    @abstractmethod
    async def save(self, tenant: Tenant) -> Tenant:
        pass

    @abstractmethod
    async def delete(self, tenant_id: int) -> bool:
        pass


# Domain Services (Complex business logic that doesn't belong to a single entity)
class TenantDomainService:
    """Service for tenant-related business logic"""

    @staticmethod
    def validate_unique_slug(slug: TenantSlug, existing_tenants: List[Tenant]) -> bool:
        """Business rule: Tenant slugs must be unique"""
        return not any(t.slug.value == slug.value for t in existing_tenants)


# Domain Events
class DomainEvent:
    """Base domain event"""
    def __init__(self):
        self.occurred_at = datetime.utcnow()


class UserCreatedEvent(DomainEvent):
    def __init__(self, user_id: int, username: str, email: str):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.email = email


class TenantCreatedEvent(DomainEvent):
    def __init__(self, tenant_id: int, slug: str):
        super().__init__()
        self.tenant_id = tenant_id
        self.slug = slug
