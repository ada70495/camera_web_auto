"""Playwright 浏览器引擎

与旧版的关键区别：不再在 import 时启动浏览器，改为由 fixture 显式创建，
并支持配置驱动的无头模式与每用例独立上下文（互不污染 cookie / 缓存）。
"""
from playwright.sync_api import sync_playwright

from common.conf_handler import config
from common.logger_handler import logger


class BrowserEngine:
    def __init__(self, headless: bool = None):
        self.playwright = sync_playwright().start()
        headless = config.headless if headless is None else headless
        self.browser = self.playwright.chromium.launch(headless=headless, slow_mo=config.slow_mo)
        logger.info(f"浏览器已启动 headless={headless} slow_mo={config.slow_mo}")

    def new_page(self, viewport: dict = None):
        """每个用例一个独立 context + page，避免用例之间串数据"""
        context = self.browser.new_context(
            viewport=viewport or {"width": 1440, "height": 900},
            ignore_https_errors=True,
        )
        page = context.new_page()
        page.set_default_timeout(config.timeout)
        return context, page

    def close(self):
        self.browser.close()
        self.playwright.stop()
        logger.info("浏览器已关闭")
