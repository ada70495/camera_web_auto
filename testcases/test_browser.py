import allure

from common.data_handler import load_test_data
from page_objects.browser_page import BrowserConfigPage

DATA = load_test_data()["browser"]


@allure.feature("浏览器配置")
class TestBrowserWeb:

    @allure.story("一键清理缓存")
    def test_clear_cache(self, page):
        browser_page = BrowserConfigPage(page)
        browser_page.enter_browser_page()

        browser_page.clear_browser_cache()
        assert browser_page.is_visible(browser_page.success_tip), "应出现「操作成功」提示"
        assert "缓存" in browser_page.get_text(browser_page.success_tip), "提示应说明缓存已清理"

    @allure.story("收藏上限配置")
    def test_collect_limit(self, page):
        browser_page = BrowserConfigPage(page)
        browser_page.enter_browser_page()

        browser_page.set_collect_limit(DATA["collect_limit"])
        assert browser_page.is_visible(browser_page.success_tip)
        assert browser_page.current_limit() == str(DATA["collect_limit"]), "收藏上限回显应与配置一致"
