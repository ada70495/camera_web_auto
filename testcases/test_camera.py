import allure

from common.conf_handler import config
from common.data_handler import load_test_data
from page_objects.camera_page import CameraConfigPage

DATA = load_test_data()["camera"]


@allure.feature("相机配置")
class TestCameraWeb:

    @allure.story("默认配置回显")
    def test_default_preview(self, page):
        cam = CameraConfigPage(page)
        cam.enter_camera_page()

        preview = cam.current_preview()
        assert DATA["default"]["resolution"] in preview, "默认分辨率应为 1080P"
        assert f"{DATA['default']['fps']}fps" in preview, "默认帧率应为 30fps"
        assert "水印关闭" in preview, "默认水印应为关闭"

    @allure.story("分辨率帧率 + 水印完整配置")
    def test_camera_full_config(self, page):
        cam = CameraConfigPage(page)
        cam.enter_camera_page()

        cam.set_camera_param(DATA["default"]["resolution"], DATA["default"]["fps"])
        cam.toggle_watermark()
        cam.select_watermark_position(DATA["position"]["bottom"])
        cam.save_config()

        assert "配置保存成功" in cam.tip_text(), "应提示配置保存成功"
        preview = cam.current_preview()
        assert DATA["default"]["resolution"] in preview, "分辨率回显应与配置一致"
        assert f"{DATA['default']['fps']}fps" in preview, "帧率回显应与配置一致"
        assert "水印开启" in preview, "水印回显应为开启"
        assert DATA["position"]["bottom_text"] in preview, "水印位置回显应为底部"

    @allure.story("切换到 4K 分辨率")
    def test_camera_switch_4k(self, page):
        cam = CameraConfigPage(page)
        cam.enter_camera_page()

        cam.set_camera_param(DATA["high"]["resolution"], DATA["high"]["fps"])
        cam.save_config()

        assert "配置保存成功" in cam.tip_text()
        preview = cam.current_preview()
        assert DATA["high"]["resolution"] in preview, "分辨率应切换为 4K"
        assert f"{DATA['high']['fps']}fps" in preview, "帧率应切换为 60fps"
        assert "水印关闭" in preview, "未开启水印时应回显关闭"

    @allure.story("帧率下限边界值")
    def test_camera_low_boundary(self, page):
        cam = CameraConfigPage(page)
        cam.enter_camera_page()

        cam.set_camera_param(DATA["low"]["resolution"], DATA["low"]["fps"])
        cam.save_config()

        assert "配置保存成功" in cam.tip_text(), "15fps 属于合法下限，应保存成功"
        preview = cam.current_preview()
        assert DATA["low"]["resolution"] in preview
        assert f"{DATA['low']['fps']}fps" in preview

    @allure.story("帧率超出上限被拦截")
    def test_camera_fps_over_limit(self, page):
        cam = CameraConfigPage(page)
        cam.enter_camera_page()

        cam.set_fps(DATA["over_limit_fps"])
        cam.save_config()

        assert "15-60" in cam.tip_text(), "超出上限应提示帧率范围"
        preview = cam.current_preview()
        assert f"{DATA['over_limit_fps']}fps" not in preview, "非法帧率不应写入回显"
        assert f"{DATA['default']['fps']}fps" in preview, "回显应保持原值"

    @allure.story("帧率低于下限被拦截")
    def test_camera_fps_under_limit(self, page):
        cam = CameraConfigPage(page)
        cam.enter_camera_page()

        cam.set_fps(DATA["under_limit_fps"])
        cam.save_config()

        assert "15-60" in cam.tip_text(), "低于下限应提示帧率范围"
        preview = cam.current_preview()
        assert f"{DATA['under_limit_fps']}fps" not in preview, "非法帧率不应写入回显"

    @allure.story("帧率为空时的提示")
    def test_camera_fps_empty(self, page):
        cam = CameraConfigPage(page)
        cam.enter_camera_page()

        cam.set_fps("")
        cam.save_config()

        assert "帧率不能为空" in cam.tip_text(), "空帧率应单独提示"

    @allure.story("水印关闭时位置不可选")
    def test_camera_position_disabled(self, page):
        cam = CameraConfigPage(page)
        cam.enter_camera_page()

        assert cam.is_position_disabled(), "未开启水印时位置下拉应为禁用状态"

    @allure.story("开启水印后可选择位置")
    def test_camera_position_enabled(self, page):
        cam = CameraConfigPage(page)
        cam.enter_camera_page()

        cam.toggle_watermark()
        assert not cam.is_position_disabled(), "开启水印后位置下拉应可用"

        cam.select_watermark_position(DATA["position"]["top"])
        cam.save_config()

        preview = cam.current_preview()
        assert "水印开启" in preview
        assert DATA["position"]["top_text"] in preview, "位置回显应为顶部"

    @allure.story("关闭水印后位置回显复位")
    def test_camera_watermark_off(self, page):
        cam = CameraConfigPage(page)
        cam.enter_camera_page()

        cam.toggle_watermark()
        cam.toggle_watermark()
        assert cam.is_position_disabled(), "关闭水印后位置下拉应恢复禁用"

        cam.save_config()
        preview = cam.current_preview()
        assert "水印关闭" in preview, "关闭水印后回显应为关闭"
        assert DATA["position"]["top_text"] not in preview, "关闭水印后不应残留位置文案"

    @allure.story("未保存的配置不生效")
    def test_camera_unsaved_change(self, page):
        cam = CameraConfigPage(page)
        cam.enter_camera_page()

        cam.set_camera_param(DATA["high"]["resolution"], DATA["high"]["fps"])
        assert "4K" in cam.page.locator(cam.resolution_select).input_value(), "下拉应已切到 4K"

        cam.reload_page()
        preview = cam.current_preview()
        assert DATA["default"]["resolution"] in preview, "重新进入页面后应回到已保存的配置"
        assert DATA["high"]["resolution"] not in preview, "未保存的分辨率不应生效"

    @allure.story("未登录访问配置页跳转登录")
    def test_camera_requires_login(self, anon_page):
        anon_page.goto(f"{config.base_url}/camera")
        assert "/login" in anon_page.url, "未登录访问配置页应跳转到登录页"
