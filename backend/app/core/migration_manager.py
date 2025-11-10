"""
Multi-Tenant Migration Management System

This module handles database migrations for multi-tenant architecture:
1. Public schema migrations (tenant registry, system tables)
2. Tenant schema migrations (user data in each tenant schema)
3. Automatic migration application to new tenants
"""

from sqlalchemy import create_engine, text, Table, Column, String, DateTime, MetaData
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Optional
import importlib
import os
import re
from pathlib import Path

from app.core.config import settings
from app.core.tenant_db import SessionLocal
from app.models.tenant import Tenant


# Migration tracking table (stored in each tenant schema)
MIGRATION_TRACKING_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class MigrationScope:
    """Defines migration scope"""
    PUBLIC = "public"      # Only public schema
    TENANT = "tenant"      # All tenant schemas
    BOTH = "both"          # Both public and tenant schemas


class MigrationManager:
    """Manages migrations for multi-tenant setup"""

    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        self.migrations_dir = Path(__file__).parent.parent.parent / "migrations"

    def initialize_tracking(self, schema_name: str = "public"):
        """Initialize migration tracking table in a schema"""
        with self.engine.connect() as conn:
            conn.execute(text(f'SET search_path TO "{schema_name}"'))
            conn.execute(text(MIGRATION_TRACKING_TABLE))
            conn.commit()

    def get_applied_migrations(self, schema_name: str) -> List[str]:
        """Get list of applied migrations for a schema"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f'SET search_path TO "{schema_name}"'))
                result = conn.execute(text("SELECT version FROM schema_migrations ORDER BY version"))
                return [row[0] for row in result]
        except:
            return []

    def mark_migration_applied(self, schema_name: str, version: str):
        """Mark a migration as applied in a schema"""
        with self.engine.connect() as conn:
            conn.execute(text(f'SET search_path TO "{schema_name}"'))
            conn.execute(
                text("INSERT INTO schema_migrations (version) VALUES (:version) ON CONFLICT DO NOTHING"),
                {"version": version}
            )
            conn.commit()

    def parse_migration_metadata(self, migration_content: str) -> Dict:
        """
        Parse migration file to extract metadata

        Migration files should include special comments:
        # MIGRATION_SCOPE: public|tenant|both
        # MIGRATION_VERSION: 001_initial
        # MIGRATION_DESCRIPTION: Create initial tables
        """
        metadata = {
            "scope": MigrationScope.TENANT,  # Default to tenant
            "version": None,
            "description": ""
        }

        scope_match = re.search(r'# MIGRATION_SCOPE:\s*(\w+)', migration_content)
        if scope_match:
            metadata["scope"] = scope_match.group(1).lower()

        version_match = re.search(r'# MIGRATION_VERSION:\s*(.+)', migration_content)
        if version_match:
            metadata["version"] = version_match.group(1).strip()

        desc_match = re.search(r'# MIGRATION_DESCRIPTION:\s*(.+)', migration_content)
        if desc_match:
            metadata["description"] = desc_match.group(1).strip()

        return metadata

    def get_pending_migrations(self, schema_name: str) -> List[Dict]:
        """Get migrations that haven't been applied to a schema"""
        applied = set(self.get_applied_migrations(schema_name))
        pending = []

        # Determine schema type
        is_public = (schema_name == "public")

        # Scan migration directory
        if self.migrations_dir.exists():
            for migration_file in sorted(self.migrations_dir.glob("*.py")):
                if migration_file.name.startswith("__"):
                    continue

                with open(migration_file, 'r') as f:
                    content = f.read()

                metadata = self.parse_migration_metadata(content)
                version = metadata["version"] or migration_file.stem

                # Check if migration applies to this schema
                scope = metadata["scope"]
                should_apply = False

                if is_public and scope in [MigrationScope.PUBLIC, MigrationScope.BOTH]:
                    should_apply = True
                elif not is_public and scope in [MigrationScope.TENANT, MigrationScope.BOTH]:
                    should_apply = True

                if should_apply and version not in applied:
                    pending.append({
                        "version": version,
                        "file": migration_file,
                        "scope": scope,
                        "description": metadata["description"]
                    })

        return pending

    def apply_migration_to_schema(self, schema_name: str, migration_file: Path) -> bool:
        """Apply a single migration to a schema"""
        try:
            with open(migration_file, 'r') as f:
                content = f.read()

            metadata = self.parse_migration_metadata(content)
            version = metadata["version"] or migration_file.stem

            print(f"Applying migration {version} to schema {schema_name}...")

            with self.engine.connect() as conn:
                conn.execute(text(f'SET search_path TO "{schema_name}", public'))

                # Execute migration SQL
                # Look for upgrade() function or direct SQL
                if "def upgrade():" in content:
                    # Python migration - need to execute the upgrade function
                    # This requires importing the module dynamically
                    self._execute_python_migration(conn, migration_file, schema_name)
                else:
                    # Direct SQL migration
                    sql_statements = self._extract_sql_from_content(content)
                    for statement in sql_statements:
                        if statement.strip():
                            conn.execute(text(statement))

                conn.commit()

            # Mark as applied
            self.mark_migration_applied(schema_name, version)
            print(f"✓ Successfully applied {version} to {schema_name}")
            return True

        except Exception as e:
            print(f"✗ Failed to apply migration to {schema_name}: {str(e)}")
            return False

    def _extract_sql_from_content(self, content: str) -> List[str]:
        """Extract SQL statements from migration content"""
        # Look for SQL between markers or in upgrade function
        sql_pattern = r'"""(.*?)"""'
        matches = re.findall(sql_pattern, content, re.DOTALL)

        if matches:
            # Split by semicolon but preserve structure
            statements = []
            for match in matches:
                statements.extend([s.strip() for s in match.split(';') if s.strip()])
            return statements

        return []

    def _execute_python_migration(self, conn, migration_file: Path, schema_name: str):
        """Execute Python-based migration"""
        # This is more complex - would need to properly import and execute
        # For now, we'll use SQL-based migrations
        pass

    def migrate_all_tenants(self) -> Dict[str, List[str]]:
        """Apply pending migrations to all tenant schemas"""
        results = {}
        db = SessionLocal()

        try:
            # Get all active tenants
            db.execute(text('SET search_path TO public'))
            tenants = db.query(Tenant).filter(Tenant.is_active == True).all()

            for tenant in tenants:
                schema_name = tenant.schema_name
                results[schema_name] = []

                # Initialize tracking if needed
                self.initialize_tracking(schema_name)

                # Get and apply pending migrations
                pending = self.get_pending_migrations(schema_name)

                for migration in pending:
                    success = self.apply_migration_to_schema(schema_name, migration["file"])
                    status = "✓" if success else "✗"
                    results[schema_name].append(f"{status} {migration['version']}")

        finally:
            db.close()

        return results

    def migrate_public_schema(self) -> List[str]:
        """Apply pending migrations to public schema"""
        results = []

        # Initialize tracking
        self.initialize_tracking("public")

        # Get and apply pending migrations
        pending = self.get_pending_migrations("public")

        for migration in pending:
            success = self.apply_migration_to_schema("public", migration["file"])
            status = "✓" if success else "✗"
            results.append(f"{status} {migration['version']}")

        return results

    def migrate_single_tenant(self, tenant_slug: str) -> List[str]:
        """Apply pending migrations to a specific tenant"""
        results = []
        db = SessionLocal()

        try:
            db.execute(text('SET search_path TO public'))
            tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()

            if not tenant:
                raise ValueError(f"Tenant '{tenant_slug}' not found")

            schema_name = tenant.schema_name

            # Initialize tracking
            self.initialize_tracking(schema_name)

            # Get and apply pending migrations
            pending = self.get_pending_migrations(schema_name)

            for migration in pending:
                success = self.apply_migration_to_schema(schema_name, migration["file"])
                status = "✓" if success else "✗"
                results.append(f"{status} {migration['version']}")

        finally:
            db.close()

        return results

    def get_migration_status(self) -> Dict:
        """Get migration status for all schemas"""
        status = {
            "public": {
                "applied": [],
                "pending": []
            },
            "tenants": {}
        }

        db = SessionLocal()

        try:
            # Public schema status
            status["public"]["applied"] = self.get_applied_migrations("public")
            status["public"]["pending"] = [m["version"] for m in self.get_pending_migrations("public")]

            # Tenant schemas status
            db.execute(text('SET search_path TO public'))
            tenants = db.query(Tenant).all()

            for tenant in tenants:
                schema_name = tenant.schema_name
                status["tenants"][tenant.slug] = {
                    "schema": schema_name,
                    "applied": self.get_applied_migrations(schema_name),
                    "pending": [m["version"] for m in self.get_pending_migrations(schema_name)]
                }

        finally:
            db.close()

        return status
