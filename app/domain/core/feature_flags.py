from app.domain.core.config import settings
from app.domain.core.enums import Environment

class FeatureFlags:
    @property
    def is_development(self) -> bool:
        return settings.ENVIRONMENT == Environment.DEVELOPMENT.value

    @property
    def is_production(self) -> bool:
        return settings.ENVIRONMENT == Environment.PRODUCTION.value