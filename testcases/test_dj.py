import allure

from common.data_handler import load_test_data
from page_objects.dj_page import DjPlayerPage

DATA = load_test_data()["dj"]


@allure.feature("DJ音乐播放器")
class TestDjWeb:

    @allure.story("歌单展示与播放")
    def test_dj_playlist_and_play(self, page):
        dj = DjPlayerPage(page)
        dj.enter_dj_page()

        assert dj.song_count() == 3, "歌单应有 3 首歌曲"

        dj.play_first_song()
        tip = dj.get_text(dj.tip)
        assert "正在播放" in tip, f"应提示正在播放，实际：{tip}"
        assert "夜航" in tip, "应播放第一首歌「夜航」"

    @allure.story("音量 / 均衡器 / 播放模式设置")
    def test_dj_settings(self, page):
        dj = DjPlayerPage(page)
        dj.enter_dj_page()

        dj.set_volume(DATA["volume"])
        dj.set_eq(DATA["eq"])
        dj.set_play_mode(DATA["play_mode"])
        dj.save_setting()

        assert dj.is_visible(dj.save_tip), "应出现「设置成功」提示"
        status = dj.current_status()
        assert str(DATA["volume"]) in status, f"音量回显应与配置一致，实际：{status}"
        assert DATA["eq_text"] in status, "均衡器回显应与配置一致"
        assert DATA["play_mode_text"] in status, "播放模式回显应与配置一致"
