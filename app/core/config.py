from urllib.parse import quote

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "UAE E-Invoicing Backend"
    database_url: str | None = None
    default_connection: str = (
        "Host=46.202.168.160;Port=5433;Username=devuser;Password=devpassword;Database=Book a demo"
    )
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_address: str = ""
    smtp_from_name: str = "UAE E-Invoicing"
    smtp_use_tls: bool = True
    smtp_suppress_send: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        parts: dict[str, str] = {}
        for token in self.default_connection.split(";"):
            if "=" in token:
                key, value = token.split("=", 1)
                parts[key.strip().lower()] = value.strip()

        host = parts.get("host", "localhost")
        port = parts.get("port", "5432")
        username = quote(parts.get("username", "postgres"), safe="")
        password = quote(parts.get("password", "postgres"), safe="")
        database = quote(parts.get("database", "postgres"), safe="")

        return f"postgresql+psycopg://{username}:{password}@{host}:{port}/{database}"


settings = Settings()
