from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Sports Program API"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./sports_program.db"
    
    class Config:
        env_file = ".env"


settings = Settings()
