from page_objects.base_page import BasePage

class AlbumManagePage(BasePage):
    # 页面固定地址
    url = "https://admin-test.xxx.com/album"
    # 全部元素定位器
    search_input = "//input[@placeholder='搜索相册名称']"
    upload_btn = "//button[text()='上传图片']"
    all_check = "//input[@class='all-check']"
    batch_delete_btn = "//button[text()='批量删除']"
    confirm_btn = "//div[text()='确认']"
    success_tip = "//div[contains(text(),'删除成功')]"

    def enter_album_page(self):
        """进入相册管理后台页面"""
        self.open_url(self.url)

    def search_album_name(self, name):
        """根据相册名称搜索"""
        self.input_text(self.search_input, name)
        self.click_element("//button[text()='搜索']")

    def open_upload_popup(self):
        """唤起图片上传弹窗"""
        self.click_element(self.upload_btn)

    def batch_delete_album(self):
        """批量选中相册并删除，完整操作链路"""
        self.click_element(self.all_check)
        self.click_element(self.batch_delete_btn)
        self.click_element(self.confirm_btn)
        # 等待成功弹窗，保证操作执行完成
        self.wait_tips(self.success_tip)