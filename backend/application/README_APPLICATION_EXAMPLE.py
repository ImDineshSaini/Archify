"""
Application layer - Use cases / Business operations

This layer:
- Orchestrates domain entities
- Uses repositories via interfaces
- Handles transactions
- Emits events
- Independent of web framework
"""

from typing import Optional
from dataclasses import dataclass

from domain.README_DOMAIN_EXAMPLE import (
    User, Tenant, Email, TenantSlug,
    IUserRepository, ITenantRepository,
    UserCreatedEvent, TenantCreatedEvent
)


# DTOs (Data Transfer Objects)
@dataclass
class LoginCommand:
    """Input for login use case"""
    username: str
    password: str
    tenant_slug: Optional[str] = None


@dataclass
class LoginResult:
    """Output from login use case"""
    access_token: str
    user_id: int
    username: str
    is_admin: bool
    tenant_slug: Optional[str] = None


@dataclass
class CreateTenantCommand:
    name: str
    slug: str
    admin_email: str
    admin_password: str


@dataclass
class CreateTenantResult:
    tenant_id: int
    slug: str
    schema_name: str
    admin_user_id: int


# Use Cases
class LoginUseCase:
    """
    Login use case - Handles authentication logic

    Benefits:
    - Testable without HTTP layer
    - Reusable (could be called from CLI, API, etc.)
    - Clear business logic
    - Easy to mock dependencies
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: 'IPasswordService',
        token_service: 'ITokenService'
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.token_service = token_service

    async def execute(self, command: LoginCommand) -> LoginResult:
        """Execute login use case"""

        # 1. Find user
        user = await self.user_repository.find_by_username(command.username)
        if not user:
            raise UserNotFoundException("User not found")

        # 2. Verify password
        if not self.password_service.verify(command.password, user.hashed_password):
            raise InvalidCredentialsException("Invalid password")

        # 3. Check if user can login (business rule)
        if not user.can_login():
            raise UserInactiveException("User account is inactive")

        # 4. Generate token
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "is_admin": user.is_admin(),
            "tenant_slug": command.tenant_slug
        }
        access_token = self.token_service.create_token(token_data)

        # 5. Return result
        return LoginResult(
            access_token=access_token,
            user_id=user.id,
            username=user.username,
            is_admin=user.is_admin(),
            tenant_slug=command.tenant_slug
        )


class CreateTenantUseCase:
    """
    Create tenant use case - Handles tenant creation

    Benefits:
    - Transaction management
    - Event emission
    - Complex orchestration
    - Rollback on failure
    """

    def __init__(
        self,
        tenant_repository: ITenantRepository,
        user_repository: IUserRepository,
        schema_service: 'ISchemaService',
        migration_service: 'IMigrationService',
        event_bus: 'IEventBus',
        unit_of_work: 'IUnitOfWork'
    ):
        self.tenant_repository = tenant_repository
        self.user_repository = user_repository
        self.schema_service = schema_service
        self.migration_service = migration_service
        self.event_bus = event_bus
        self.unit_of_work = unit_of_work

    async def execute(self, command: CreateTenantCommand) -> CreateTenantResult:
        """Execute create tenant use case"""

        # 1. Validate slug
        slug = TenantSlug(command.slug)
        email = Email(command.admin_email)

        # 2. Check uniqueness
        existing = await self.tenant_repository.find_by_slug(slug)
        if existing:
            raise TenantAlreadyExistsException("Tenant slug already exists")

        # 3. Start transaction
        async with self.unit_of_work:
            # 4. Create tenant entity
            tenant = Tenant(
                id=None,
                name=command.name,
                slug=slug,
                admin_email=email,
                is_active=True,
                is_trial=True
            )

            # 5. Save tenant
            tenant = await self.tenant_repository.save(tenant)

            # 6. Create schema
            schema_name = tenant.get_schema_name()
            await self.schema_service.create_schema(schema_name)

            # 7. Run migrations
            await self.migration_service.migrate_schema(schema_name)

            # 8. Create admin user in tenant schema
            admin_user = User(
                id=None,
                username=f"admin_{slug.value}",
                email=email,
                hashed_password=self.password_service.hash(command.admin_password),
                is_active=True,
                is_admin=True
            )
            admin_user = await self.user_repository.save(admin_user)

            # 9. Commit transaction
            await self.unit_of_work.commit()

            # 10. Emit events
            await self.event_bus.publish(TenantCreatedEvent(
                tenant_id=tenant.id,
                slug=slug.value
            ))
            await self.event_bus.publish(UserCreatedEvent(
                user_id=admin_user.id,
                username=admin_user.username,
                email=email.value
            ))

            # 11. Return result
            return CreateTenantResult(
                tenant_id=tenant.id,
                slug=slug.value,
                schema_name=schema_name,
                admin_user_id=admin_user.id
            )


# Service Interfaces (needed by use cases)
class IPasswordService(ABC):
    @abstractmethod
    def hash(self, password: str) -> str:
        pass

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        pass


class ITokenService(ABC):
    @abstractmethod
    def create_token(self, data: dict) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str) -> dict:
        pass


class ISchemaService(ABC):
    @abstractmethod
    async def create_schema(self, schema_name: str) -> bool:
        pass

    @abstractmethod
    async def delete_schema(self, schema_name: str) -> bool:
        pass


class IMigrationService(ABC):
    @abstractmethod
    async def migrate_schema(self, schema_name: str) -> bool:
        pass


class IEventBus(ABC):
    @abstractmethod
    async def publish(self, event: 'DomainEvent'):
        pass


class IUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass


# Custom Exceptions
class ApplicationException(Exception):
    """Base application exception"""
    pass


class UserNotFoundException(ApplicationException):
    pass


class InvalidCredentialsException(ApplicationException):
    pass


class UserInactiveException(ApplicationException):
    pass


class TenantAlreadyExistsException(ApplicationException):
    pass
