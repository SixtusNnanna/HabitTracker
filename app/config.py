import os


from dotenv import load_dotenv


class ConfigSingleton():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        load_dotenv()
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./habits.db")
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.secrets = self.require("SECRETS")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_exp_time = 30
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = os.getenv("REDIS_PORT", 6379)

    @staticmethod
    def require(key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Missing required enviroment variable: {key}")
        return value


settings = ConfigSingleton()




