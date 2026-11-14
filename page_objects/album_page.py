from page_objects.base_page import BasePage


class AlbumManagePage(BasePage):
    """相册管理页"""

    path = "/album"
    search_input = "//input[@placeholder='搜索相册名称']"
    search_btn = "//button[text()='搜索']"
    upload_btn = "//button[text()='上传图片']"
    all_check = "//input[@class='all-check']"
    batch_delete_btn = "//button[text()='批量删除']"
    confirm_btn = "//div[text()='确认']"
    success_tip = "//div[contains(text(),'删除成功')]"
    upload_tip = "//div[contains(text(),'上传成功')]"
    album_names = "//td[@class='album-name']"
    visible_rows = "//tbody[@id='albumBody']/tr[not(@hidden)]"

    def enter_album_page(self):
        self.open_url()

    def search_album_name(self, name: str):
        self.input_text(self.search_input, name)
        self.click_element(self.search_btn)

    def open_upload_popup(self):
        self.click_element(self.upload_btn)

    def batch_delete_album(self):
        """全选 → 批量删除 → 确认 → 等待删除成功提示"""
        self.click_element(self.all_check)
        self.click_element(self.batch_delete_btn)
        self.click_element(self.confirm_btn)
        self.wait_tips(self.success_tip)

    def remaining_albums(self) -> int:
        return self.count(self.visible_rows)

    def first_visible_album_name(self) -> str:
        return (
            self.page.locator(self.visible_rows).first.locator("td.album-name").text_content()
        )
