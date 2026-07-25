from page_objects.base_page import BasePage

class CameraConfigPage(BasePage):
    url = "https://admin-test.xxx.com/camera"
    resolution_select = "//select[@name='resolution']"
    fps_input = "//input[@name='fps']"
    watermark_switch = "//input[@name='watermark']"
    save_btn = "//button[text()='保存配置']"
    save_tip = "//div[contains(text(),'配置保存成功')]"

    def enter_camera_page(self):
        self.open_url(self.url)

    def set_camera_param(self, resolution, fps):
        """设置分辨率、帧率参数"""
        self.page.select_option(self.resolution_select, resolution)
        self.input_text(self.fps_input, str(fps))

    def open_watermark(self):
        """开启水印开关"""
        self.click_element(self.watermark_switch)

    def save_config(self):
        """保存配置，等待成功提示"""
        self.click_element(self.save_btn)
        self.wait_tips(self.save_tip)