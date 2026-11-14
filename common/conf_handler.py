"""配置读取：env.yaml（入库）+ env_local.yaml（本地私有，不入库）深度覆盖

优先级：环境变量 BASE_URL / ENV / HEADLESS > env_local.yaml > env.yaml
"""
import os

import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
ENV_FILE = os.path.join(CONFIG_DIR, "env.yaml")
LOCAL_ENV_FILE = os.path.join(CONFIG_DIR, "env_local.yaml")


def read_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def deep_merge(base, override):
    result = dict(base or {})
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class Config:
    def __init__(self, env=None):
        data = read_yaml(ENV_FILE)
        if os.path.exists(LOCAL_ENV_FILE):
            data = deep_merge(data, read_yaml(LOCAL_ENV_FILE))
        self._data = data
        self.env = env or os.getenv("ENV") or data.get("current_env", "local")
        if self.env not in data:
            raise ValueError(f"环境 {self.env} 未定义")
        self._env = data[self.env]

    @property
    def base_url(self) -> str:
        return (os.getenv("BASE_URL") or self._env["base_url"]).rstrip("/")

    @property
    def timeout(self) -> int:
        return self._env.get("timeout", 10000)

    @property
    def headless(self) -> bool:
        flag = os.getenv("HEADLESS")
        if flag is None:
            return bool(self._env.get("headless", True))
        return flag.strip().lower() in ("1", "true", "yes")

    @property
    def slow_mo(self) -> int:
        return int(self._env.get("slow_mo", 0))

    @property
    def account(self) -> dict:
        return self._data.get("account", {})

    @property
    def username(self) -> str:
        return os.getenv("ADMIN_USER") or self.account.get("username", "")

    @property
    def password(self) -> str:
        return os.getenv("ADMIN_PWD") or self.account.get("password", "")

    def summary(self) -> str:
        return f"ENV={self.env} BASE_URL={self.base_url} HEADLESS={self.headless} TIMEOUT={self.timeout}"


config = Config()
