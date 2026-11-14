from page_objects.base_page import BasePage


class CameraConfigPage(BasePage):
    """相机配置页"""

    path = "/camera"
    resolution_select = "//select[@name='resolution']"
    fps_input = "//input[@name='fps']"
    watermark_switch = "//input[@name='watermark']"
    save_btn = "//button[text()='保存配置']"
    save_tip = "//div[contains(text(),'配置保存成功')]"
    preview_text = "//span[@id='previewText']"

    def enter_camera_page(self):
        self.open_url()

    def set_camera_param(self, resolution: str, fps: int):
        self.select_option(self.resolution_select, resolution)
        self.input_text(self.fps_input, fps)

    def open_watermark(self):
        self.click_element(self.watermark_switch)

    def save_config(self):
        self.click_element(self.save_btn)
        self.wait_tips(self.save_tip)

    def current_preview(self) -> str:
        return self.get_text(self.preview_text)
