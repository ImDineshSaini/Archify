from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextvars import ContextVar
from app.core.config import settings

# Create engine for public schema
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Context variable to store current tenant schema
current_tenant_schema: ContextVar[str] = ContextVar('current_tenant_schema', default='public')


def get_db():
    """Dependency for getting database session with tenant context"""
    db = SessionLocal()
    try:
        # Set schema for this session based on tenant context
        schema = current_tenant_schema.get()
        if schema and schema != 'public':
            db.execute(text(f'SET search_path TO "{schema}", public'))
        yield db
    finally:
        db.close()


def get_public_db():
    """Get database session for public schema (tenant management)"""
    db = SessionLocal()
    try:
        db.execute(text('SET search_path TO public'))
        yield db
    finally:
        db.close()


class TenantDatabaseManager:
    """Manages tenant schema creation and migrations"""

    @staticmethod
    def create_tenant_schema(schema_name: str):
        """
        Create a new schema for a tenant

        This now uses migrations instead of creating tables directly.
        All pending tenant migrations will be automatically applied.
        """
        db = SessionLocal()
        try:
            # Create schema
            db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
            db.commit()

            # Apply migrations to new schema
            from app.core.migration_manager import MigrationManager

            manager = MigrationManager()
            manager.initialize_tracking(schema_name)

            # Get tenant migrations
            pending = manager.get_pending_migrations(schema_name)

            # Apply each migration
            for migration in pending:
                manager.apply_migration_to_schema(schema_name, migration["file"])

            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create tenant schema: {str(e)}")
        finally:
            db.close()

    @staticmethod
    def delete_tenant_schema(schema_name: str):
        """Delete a tenant schema and all its data"""
        if schema_name == 'public':
            raise ValueError("Cannot delete public schema")

        db = SessionLocal()
        try:
            db.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to delete tenant schema: {str(e)}")
        finally:
            db.close()

    @staticmethod
    def seed_tenant_data(schema_name: str, admin_user_data: dict):
        """Seed initial data for a new tenant"""
        db = SessionLocal()
        try:
            from app.models.user import User
            from app.core.security import get_password_hash

            # Set search path to tenant schema
            db.execute(text(f'SET search_path TO "{schema_name}", public'))

            # Create admin user
            admin_user = User(
                email=admin_user_data['email'],
                username=admin_user_data['username'],
                full_name=admin_user_data.get('full_name'),
                hashed_password=get_password_hash(admin_user_data['password']),
                is_active=True,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()

            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to seed tenant data: {str(e)}")
        finally:
            db.close()
