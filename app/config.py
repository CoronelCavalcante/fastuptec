from pydantic import BaseSettings
#arquivo usado para organizar as configuraçoes ambientais que serao usadas para acessar o banco de dados

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_name: str
    database_username: str
    database_password: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    ixc_token: str
    class Config:
        env_file = '.env'

settings = Settings()

