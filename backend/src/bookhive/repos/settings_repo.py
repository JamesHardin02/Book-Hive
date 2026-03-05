from __future__ import annotations

from bookhive.db.models.app_setting import AppSetting
from sqlalchemy.orm import Session


class SettingsRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_int(self, key: str) -> int | None:
        row = self.db.query(AppSetting).filter(AppSetting.key == key).first()
        return None if row is None else row.int_value

    def set_int(self, key: str, value: int) -> None:
        row = self.db.query(AppSetting).filter(AppSetting.key == key).first()
        if row:
            row.int_value = value
        else:
            self.db.add(AppSetting(key=key, int_value=value))
        self.db.commit()
