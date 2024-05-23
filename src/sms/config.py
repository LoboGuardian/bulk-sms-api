import os
from dotenv import load_dotenv

load_dotenv()


class Config:
	CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL")


settings = Config()
