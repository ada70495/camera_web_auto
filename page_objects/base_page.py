from playwright.sync_api import Page

from common.conf_handler import config
from common.logger_handler import logger


class BasePage:
    """PO 模式公共父类：封装所有页面通用操作 + 显式等待"""

    path = "/"

    def __init__(self, page: Page):
        self.page = page

    @property
    def url(self) -> str:
        """页面完整地址 = 环境地址 + 页面路径，环境切换只改配置"""
        return config.base_url + self.path

    def open_url(self, url: str = None):
        target = url or self.url
        self.page.goto(target)
        self.page.wait_for_load_state("networkidle")
        logger.info(f"打开页面：{target}")

    def click_element(self, locator: str, timeout: int = None):
        """先等待元素出现再点击，解决元素未加载就点击的报错"""
        self.page.wait_for_selector(locator, timeout=timeout or config.timeout)
        self.page.click(locator)

    def input_text(self, locator: str, value, timeout: int = None):
        self.page.wait_for_selector(locator, timeout=timeout or config.timeout)
        self.page.fill(locator, str(value))

    def select_option(self, locator: str, value: str):
        self.page.wait_for_selector(locator)
        self.page.select_option(locator, value)

    def get_text(self, locator: str) -> str:
        return self.page.locator(locator).text_content()

    def count(self, locator: str) -> int:
        return self.page.locator(locator).count()

    def is_visible(self, locator: str) -> bool:
        return self.page.locator(locator).is_visible()

    def wait_tips(self, locator: str, timeout: int = None):
        """等待操作结果提示出现"""
        self.page.wait_for_selector(locator, timeout=timeout or config.timeout)
        logger.info(f"提示已出现：{locator}")

    def screenshot(self, path: str):
        self.page.screenshot(path=path, full_page=True)
        logger.info(f"截图已保存：{path}")
