"""YAML 测试数据读取"""
import os

import yaml

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_test_data(name: str = "test_data.yaml") -> dict:
    path = os.path.join(DATA_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
