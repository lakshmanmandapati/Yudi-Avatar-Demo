import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None
    GOOGLE_APPLICATION_CREDENTIALS_JSON: str | None = None

    GOOGLE_SHEETS_SPREADSHEET_ID: str = ""
    GOOGLE_SHEETS_RANGE: str = "Sheet1!A:F"

    ALLOWED_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# If credentials JSON is provided in env, write to a temp path so Google libs can pick it up.
if settings.GOOGLE_APPLICATION_CREDENTIALS_JSON and not settings.GOOGLE_APPLICATION_CREDENTIALS:
    path = "/tmp/gcp_creds.json"
    with open(path, "w") as f:
        f.write(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
elif settings.GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
