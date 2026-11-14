import allure

from common.data_handler import load_test_data
from page_objects.camera_page import CameraConfigPage

DATA = load_test_data()["camera"]


@allure.feature("相机配置")
class TestCameraWeb:

    @allure.story("分辨率帧率 + 水印完整配置")
    def test_camera_full_config(self, page):
        """完整流程：进相机页 → 设置 1080P/30帧 → 开水印 → 保存 → 断言回显"""
        cam = CameraConfigPage(page)
        cam.enter_camera_page()

        cam.set_camera_param(DATA["default"]["resolution"], DATA["default"]["fps"])
        cam.open_watermark()
        cam.save_config()

        assert cam.is_visible(cam.save_tip), "应出现「配置保存成功」提示"
        preview = cam.current_preview()
        assert DATA["default"]["resolution"] in preview, "分辨率回显应与配置一致"
        assert f"{DATA['default']['fps']}fps" in preview, "帧率回显应与配置一致"
        assert "水印开启" in preview, "水印回显应为开启"

    @allure.story("切换到 4K 分辨率")
    def test_camera_switch_4k(self, page):
        cam = CameraConfigPage(page)
        cam.enter_camera_page()

        cam.set_camera_param(DATA["high"]["resolution"], DATA["high"]["fps"])
        cam.save_config()

        assert cam.is_visible(cam.save_tip)
        preview = cam.current_preview()
        assert DATA["high"]["resolution"] in preview, "分辨率应切换为 4K"
        assert f"{DATA['high']['fps']}fps" in preview, "帧率应切换为 60fps"
        assert "水印关闭" in preview, "默认水印为关闭状态"
