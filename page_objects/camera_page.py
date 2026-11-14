from page_objects.base_page import BasePage


class CameraConfigPage(BasePage):
    """相机配置页"""

    path = "/camera"
    resolution_select = "//select[@name='resolution']"
    fps_input = "//input[@name='fps']"
    watermark_switch = "//input[@name='watermark']"
    watermark_position = "//select[@name='watermark_position']"
    save_btn = "//button[text()='保存配置']"
    tip = "//div[@id='tip']"
    preview_text = "//span[@id='previewText']"

    def enter_camera_page(self):
        self.open_url()

    def set_resolution(self, resolution: str):
        self.select_option(self.resolution_select, resolution)

    def set_fps(self, fps):
        self.input_text(self.fps_input, fps)

    def set_camera_param(self, resolution: str, fps):
        """一次设置分辨率与帧率"""
        self.set_resolution(resolution)
        self.set_fps(fps)

    def toggle_watermark(self):
        """点击水印开关，切换开/关"""
        self.click_element(self.watermark_switch)

    def select_watermark_position(self, position: str):
        self.select_option(self.watermark_position, position)

    def is_position_disabled(self) -> bool:
        return self.page.locator(self.watermark_position).is_disabled()

    def save_config(self):
        self.click_element(self.save_btn)
        self.wait_tips(self.tip)

    def tip_text(self) -> str:
        return self.get_text(self.tip)

    def current_preview(self) -> str:
        return self.get_text(self.preview_text)

    def reload_page(self):
        self.page.reload()
        self.page.wait_for_load_state("networkidle")
