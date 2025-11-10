"""
Database migrations for Archify

Migration files should include metadata comments:

# MIGRATION_SCOPE: public|tenant|both
# MIGRATION_VERSION: 001_migration_name
# MIGRATION_DESCRIPTION: What this migration does

Example:
```python
# MIGRATION_SCOPE: tenant
# MIGRATION_VERSION: 003_add_user_avatar
# MIGRATION_DESCRIPTION: Add avatar_url column to users table

UPGRADE_SQL = '''
ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500);
'''

DOWNGRADE_SQL = '''
ALTER TABLE users DROP COLUMN avatar_url;
'''
```
"""
