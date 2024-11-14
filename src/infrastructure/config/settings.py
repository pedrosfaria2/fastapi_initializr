from pydantic import Field
from pydantic_settings import BaseSettings
from loguru import logger
from sys import stderr
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    ENVIRONMENT: str = Field(
        default="dev",
        description="Environment (dev, test, prod)",
    )
    APP_NAME: str = Field(
        default="FastAPI Initializr",
        description="Application name",
    )
    APP_VERSION: str = Field(
        default="0.1.0",
        description="Application version",
    )

    def configure_logging(self):
        if not logger._core.handlers:
            logger.add(
                sink=stderr,
                colorize=True,
                level="DEBUG" if self.ENVIRONMENT != "production" else "INFO",
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            )
            logger.info(
                f"Environment {self.ENVIRONMENT} initialized for {self.APP_NAME} v{self.APP_VERSION}"
            )


settings = Settings()
settings.configure_logging()
