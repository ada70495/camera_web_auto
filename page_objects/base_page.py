from playwright.sync_api import Page
from common.logger_handler import logger

class BasePage:
    """PO模式公共父类，封装所有页面通用操作"""
    def __init__(self, page: Page):
        self.page = page

    def open_url(self, url):
        """打开指定页面，等待页面网络空闲，保证加载完成"""
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
        logger.info(f"打开页面地址：{url}")

    def click_element(self, locator, timeout=10000):
        """点击元素：先等待元素出现再点击，解决元素未加载点击报错"""
        self.page.wait_for_selector(locator, timeout=timeout)
        self.page.click(locator)

    def input_text(self, locator, value, timeout=10000):
        """输入文本：等待元素可输入再填充内容"""
        self.page.wait_for_selector(locator, timeout=timeout)
        self.page.fill(locator, value)

    def get_text(self, locator):
        """获取元素文本内容"""
        return self.page.locator(locator).text_content()

    def wait_tips(self, locator):
        """等待弹窗提示出现，用于校验操作成功弹窗"""
        self.page.wait_for_selector(locator, timeout=10000)