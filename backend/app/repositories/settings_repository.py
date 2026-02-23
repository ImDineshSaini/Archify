"""Repository for SystemSettings entity."""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.settings import SystemSettings


class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_key(self, key: str) -> Optional[SystemSettings]:
        return self.db.query(SystemSettings).filter(
            SystemSettings.key == key
        ).first()

    def get_all(self):
        return self.db.query(SystemSettings).all()

    def upsert(
        self,
        key: str,
        value: str,
        description: str = "",
        is_encrypted: bool = False,
    ) -> SystemSettings:
        setting = self.get_by_key(key)
        if setting:
            setting.value = value
        else:
            setting = SystemSettings(
                key=key,
                value=value,
                description=description,
                is_encrypted=is_encrypted,
            )
            self.db.add(setting)
        return setting
