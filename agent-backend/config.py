from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    # JWT Authentication
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Application settings
    environment: str = "development"
    debug: bool = False
    frontend_url: str = "http://localhost:3000"
    upload_directory: str = "./uploads"
    allowed_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        alias="allowed_origins"
    )

    # External API settings
    JOB_APPLY_API_BASE: str | None = None
    JOB_APPLY_API_KEY: str | None = None

    @property
    def allowed_origins(self) -> list[str]:
        """Parse allowed_origins as a comma-separated list"""
        return [origin.strip() for origin in self.allowed_origins_str.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
    )


settings = Settings()  # type: ignore[call-arg]
