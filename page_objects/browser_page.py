from page_objects.base_page import BasePage


class BrowserConfigPage(BasePage):
    """浏览器配置页"""

    path = "/browser"
    clear_cache_btn = "//button[text()='一键清理缓存']"
    collect_max_input = "//input[@name='collect_max']"
    save_btn = "//button[text()='保存']"
    success_tip = "//div[contains(text(),'操作成功')]"
    max_text = "//span[@id='maxText']"

    def enter_browser_page(self):
        self.open_url()

    def clear_browser_cache(self):
        self.click_element(self.clear_cache_btn)
        self.wait_tips(self.success_tip)

    def set_collect_limit(self, num: int):
        self.input_text(self.collect_max_input, num)
        self.click_element(self.save_btn)
        self.wait_tips(self.success_tip)

    def current_limit(self) -> str:
        return self.get_text(self.max_text)
