from page_objects.base_page import BasePage

class BrowserConfigPage(BasePage):
    url = "https://admin-test.xxx.com/browser"
    clear_cache_btn = "//button[text()='一键清理缓存']"
    collect_max_input = "//input[@name='collect_max']"
    save_btn = "//button[text()='保存']"
    success_tip = "//div[contains(text(),'操作成功')]"

    def enter_browser_page(self):
        self.open_url(self.url)

    def clear_browser_cache(self):
        """一键清理浏览器后台缓存配置"""
        self.click_element(self.clear_cache_btn)
        self.wait_tips(self.success_tip)

    def set_collect_limit(self, num):
        """设置浏览器最大收藏数量"""
        self.input_text(self.collect_max_input, str(num))
        self.click_element(self.save_btn)