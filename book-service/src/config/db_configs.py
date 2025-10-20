from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    db_url: str
    db_username: str
    db_password: str
    db_host: str
    db_name: str

@dataclass
class PoolConfig:
    pool_size: int = 10
    max_overflows: int = 1
    pool_timeout: int = 10
    pool_recycle: int = 10
    pool_pre_ping: int = 10
    echo: bool = False
    echo_pool: bool = False
    hide_parameters: bool = True

@dataclass
class ConnectionConfig:
    max_connections_retries: int = 5
    retry_delay: int = 3