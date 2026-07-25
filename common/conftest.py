import pytest
from common.browser_handler import web_driver

@pytest.fixture(scope="session", autouse=True)
def web_setup():
    # 全局把page对象传给所有用例
    yield web_driver.page
    # 全部用例结束关闭浏览器
    web_driver.close_all()