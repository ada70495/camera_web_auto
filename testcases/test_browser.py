from page_objects.browser_page import BrowserConfigPage

class TestBrowserWeb:
    def test_browser_cache_and_collect(self, page):
        """浏览器后台：清理缓存+配置收藏上限"""
        browser = BrowserConfigPage(page)
        browser.enter_browser_page()
        browser.clear_browser_cache()
        browser.set_collect_limit(200)