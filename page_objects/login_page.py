from page_objects.base_page import BasePage


class LoginPage(BasePage):
    """后台登录页"""

    path = "/login"
    username_input = "//input[@name='username']"
    password_input = "//input[@name='password']"
    submit_btn = "//button[@type='submit']"
    error_tip = "//div[contains(text(),'用户名或密码错误')]"

    def login(self, username: str, password: str):
        self.open_url()
        self.input_text(self.username_input, username)
        self.input_text(self.password_input, password)
        self.click_element(self.submit_btn)
        self.page.wait_for_load_state("networkidle")
