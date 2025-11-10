"""
Migration CLI commands

Usage:
  python -m app.cli.migrate status              # Show migration status
  python -m app.cli.migrate public              # Migrate public schema
  python -m app.cli.migrate tenants             # Migrate all tenant schemas
  python -m app.cli.migrate tenant <slug>       # Migrate specific tenant
  python -m app.cli.migrate all                 # Migrate everything
"""

import sys
import argparse
from app.core.migration_manager import MigrationManager


def status():
    """Show migration status for all schemas"""
    manager = MigrationManager()
    status = manager.get_migration_status()

    print("\n" + "=" * 60)
    print("MIGRATION STATUS")
    print("=" * 60)

    # Public schema
    print("\n📊 Public Schema:")
    print(f"  Applied: {len(status['public']['applied'])}")
    print(f"  Pending: {len(status['public']['pending'])}")

    if status['public']['applied']:
        print("\n  Applied migrations:")
        for version in status['public']['applied']:
            print(f"    ✓ {version}")

    if status['public']['pending']:
        print("\n  Pending migrations:")
        for version in status['public']['pending']:
            print(f"    ⏳ {version}")

    # Tenant schemas
    print(f"\n🏢 Tenant Schemas: {len(status['tenants'])}")
    for tenant_slug, tenant_status in status['tenants'].items():
        print(f"\n  {tenant_slug} ({tenant_status['schema']}):")
        print(f"    Applied: {len(tenant_status['applied'])}")
        print(f"    Pending: {len(tenant_status['pending'])}")

        if tenant_status['pending']:
            for version in tenant_status['pending']:
                print(f"      ⏳ {version}")

    print("\n" + "=" * 60 + "\n")


def migrate_public():
    """Migrate public schema"""
    print("\n🔄 Migrating public schema...")
    manager = MigrationManager()
    results = manager.migrate_public_schema()

    if results:
        print("\nResults:")
        for result in results:
            print(f"  {result}")
    else:
        print("  No pending migrations")

    print("\n✅ Public schema migration complete\n")


def migrate_tenants():
    """Migrate all tenant schemas"""
    print("\n🔄 Migrating all tenant schemas...")
    manager = MigrationManager()
    results = manager.migrate_all_tenants()

    if results:
        for schema, migrations in results.items():
            print(f"\n  {schema}:")
            if migrations:
                for migration in migrations:
                    print(f"    {migration}")
            else:
                print("    No pending migrations")
    else:
        print("  No tenants found")

    print("\n✅ Tenant migration complete\n")


def migrate_tenant(tenant_slug: str):
    """Migrate specific tenant schema"""
    print(f"\n🔄 Migrating tenant: {tenant_slug}...")
    manager = MigrationManager()

    try:
        results = manager.migrate_single_tenant(tenant_slug)

        if results:
            print("\nResults:")
            for result in results:
                print(f"  {result}")
        else:
            print("  No pending migrations")

        print(f"\n✅ Tenant {tenant_slug} migration complete\n")

    except ValueError as e:
        print(f"\n✗ Error: {str(e)}\n")
        sys.exit(1)


def migrate_all():
    """Migrate everything (public + all tenants)"""
    print("\n🔄 Migrating all schemas...")

    # Migrate public first
    migrate_public()

    # Then migrate tenants
    migrate_tenants()

    print("✅ All migrations complete\n")


def main():
    parser = argparse.ArgumentParser(description='Database migration manager')
    parser.add_argument('command',
                       choices=['status', 'public', 'tenants', 'tenant', 'all'],
                       help='Migration command')
    parser.add_argument('tenant_slug', nargs='?', help='Tenant slug (for tenant command)')

    args = parser.parse_args()

    if args.command == 'status':
        status()
    elif args.command == 'public':
        migrate_public()
    elif args.command == 'tenants':
        migrate_tenants()
    elif args.command == 'tenant':
        if not args.tenant_slug:
            print("Error: tenant slug required")
            sys.exit(1)
        migrate_tenant(args.tenant_slug)
    elif args.command == 'all':
        migrate_all()


if __name__ == '__main__':
    main()
