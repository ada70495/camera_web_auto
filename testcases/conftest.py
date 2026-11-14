"""全局 fixture：浏览器引擎 / 页面 / 登录 / 站点数据复位"""
import os
import sys

import pytest
import requests

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from common.conf_handler import config
from common.logger_handler import logger
from page_objects.login_page import LoginPage


@pytest.fixture(scope="session", autouse=True)
def site_ready():
    """执行前先确认站点在线并复位数据"""
    try:
        resp = requests.post(f"{config.base_url}/__admin/reset", timeout=5)
    except requests.ConnectionError:
        raise RuntimeError(
            f"后台站点未启动：{config.base_url}\n请先执行：python mock_site/app.py"
        )
    assert resp.status_code == 200, "站点数据复位失败"
    logger.info(f"测试环境：{config.summary()}")
    yield


@pytest.fixture(scope="session")
def engine():
    """整个 session 只启动一次浏览器"""
    from common.browser_handler import BrowserEngine

    browser = BrowserEngine()
    yield browser
    browser.close()


@pytest.fixture()
def page(engine):
    """每个用例独立 context + page，并在测试前完成登录"""
    context, page = engine.new_page()
    LoginPage(page).login(config.username, config.password)
    yield page
    context.close()


@pytest.fixture()
def anon_page(engine):
    """未登录页面，用于验证登录拦截"""
    context, page = engine.new_page()
    yield page
    context.close()


@pytest.fixture()
def fresh_site():
    """破坏性用例（如批量删除）执行前复位站点数据"""
    requests.post(f"{config.base_url}/__admin/reset", timeout=5)
