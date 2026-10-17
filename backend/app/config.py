import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://traceforge:traceforge@localhost:5432/traceforge"
    secret_key: str
    allowed_origins: str = "http://localhost:3000"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    
    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.secret_key == "changeme":
            raise ValueError("SECRET_KEY must be changed from default")

settings = Settings()
