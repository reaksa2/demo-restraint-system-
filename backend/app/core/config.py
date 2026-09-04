from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central app configuration, loaded from environment variables / .env file.
    Nothing here should be hardcoded elsewhere in the app.
    """

    DATABASE_URL: str = "postgresql://menu_user:menu_password@localhost:5432/restaurant_menu"

    SECRET_KEY: str = "insecure-dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    SEED_LEVEL1_EMAIL: str = "owner@example.com"
    SEED_LEVEL1_PASSWORD: str = "change-me-now"
    SEED_LEVEL1_NAME: str = "System Owner"

    UPLOAD_DIR: str = "uploads"
    UPLOAD_URL_PREFIX: str = "/static/uploads"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
