from page_objects.base_page import BasePage


class DjPlayerPage(BasePage):
    """DJ 音乐播放器页"""

    path = "/dj"
    first_play_btn = "(//button[@class='play-btn'])[1]"
    volume_input = "//input[@name='volume']"
    eq_select = "//select[@name='eq']"
    play_mode_select = "//select[@name='play_mode']"
    save_btn = "//button[text()='保存设置']"
    tip = "//div[@id='tip']"
    play_tip = "//div[contains(text(),'正在播放')]"
    save_tip = "//div[contains(text(),'设置成功')]"
    status_text = "//span[@id='statusText']"
    song_rows = "//tbody[@id='playlist']/tr"

    def enter_dj_page(self):
        self.open_url()

    def play_first_song(self):
        self.click_element(self.first_play_btn)
        self.wait_tips(self.play_tip)

    def set_volume(self, volume: int):
        self.input_text(self.volume_input, volume)

    def set_eq(self, mode: str):
        self.select_option(self.eq_select, mode)

    def set_play_mode(self, mode: str):
        self.select_option(self.play_mode_select, mode)

    def save_setting(self):
        self.click_element(self.save_btn)
        self.wait_tips(self.save_tip)

    def current_status(self) -> str:
        return self.get_text(self.status_text)

    def song_count(self) -> int:
        return self.count(self.song_rows)
