from page_objects.camera_page import CameraConfigPage

class TestCameraWeb:
    def test_camera_full_config(self, page):
        """完整配置流程：进相机页→设置分辨率帧率→开水印→保存"""
        cam = CameraConfigPage(page)
        cam.enter_camera_page()
        cam.set_camera_param("1080P", 30)
        cam.open_watermark()
        cam.save_config()