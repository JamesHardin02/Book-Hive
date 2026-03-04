from __future__ import annotations

from bookhive.repos.settings_repo import SettingsRepo

LOW_STOCK_KEY = "low_stock_threshold"


class SettingsService:
    def __init__(self, repo: SettingsRepo):
        self.repo = repo

    def get_low_stock_threshold(self) -> int:
        v = self.repo.get_int(LOW_STOCK_KEY)
        return 2 if v is None else v

    def set_low_stock_threshold(self, threshold: int) -> None:
        self.repo.set_int(LOW_STOCK_KEY, threshold)
