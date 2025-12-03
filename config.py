import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        SECRET_KEY = "dev-secret-key-change-in-production"


class DevelopmentConfig(Config):
    DEBUG = True
    PG_HOST = os.environ.get("PGHOST")
    PG_USER = os.environ.get("PGUSER")
    PG_PASSWORD = os.environ.get("PGPASSWORD")
    PG_DB = os.environ.get("PGDATABASE")
    PG_PORT = int(os.environ.get("PGPORT", "5432"))


class ProductionConfig(Config):
    DEBUG = False
    PG_HOST = os.environ.get("PGHOST")
    PG_USER = os.environ.get("PGUSER")
    PG_PASSWORD = os.environ.get("PGPASSWORD")
    PG_DB = os.environ.get("PGDATABASE")
    PG_PORT = int(os.environ.get("PGPORT", "5432"))


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
