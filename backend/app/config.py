from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./traceforge.db"
    secret_key: str = "local-development-secret"
    allowed_origins: str = "http://localhost:3000"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.secret_key in {
            "changeme",
            "CHANGE_THIS_TO_RANDOM_STRING_IN_PRODUCTION",
        }:
            raise ValueError("SECRET_KEY must be changed from default")


settings = Settings()
