from playwright.sync_api import sync_playwright

class BrowserEngine:
    def __init__(self):
        # 启动playwright引擎
        self.play = sync_playwright().start()
        # 启动chrome浏览器，headless=False可视化调试，上线改为True无头
        self.browser = self.play.chromium.launch(headless=False)
        # 创建浏览器上下文（可隔离cookie、缓存）
        self.context = self.browser.new_context()
        # 新建标签页
        self.page = self.context.new_page()

    def close_all(self):
        # 全部用例跑完关闭浏览器、引擎
        self.browser.close()
        self.play.stop()

# 全局唯一浏览器实例
web_driver = BrowserEngine()