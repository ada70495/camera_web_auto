import allure

from common.data_handler import load_test_data
from page_objects.album_page import AlbumManagePage

DATA = load_test_data()


@allure.feature("相册管理")
class TestAlbumWeb:

    @allure.story("相册检索与批量删除")
    def test_album_batch_delete(self, page, fresh_site):
        """完整链路：进相册页 → 检索 → 全选 → 批量删除 → 断言结果"""
        album = AlbumManagePage(page)
        album.enter_album_page()
        assert album.remaining_albums() == DATA["album"]["initial_count"], "初始相册数量应与数据文件一致"

        album.search_album_name(DATA["album"]["search_keyword"])
        assert album.remaining_albums() == 1, "检索后应只剩 1 个相册"
        assert (
            album.first_visible_album_name() == DATA["album"]["search_keyword"]
        ), "检索结果应与关键字一致"

        album.batch_delete_album()
        assert album.is_visible(album.success_tip), "应出现「删除成功」提示"
        assert album.remaining_albums() == 0, "删除后列表应为空"

    @allure.story("图片上传入口")
    def test_album_upload_entry(self, page):
        """点击上传按钮后，页面给出上传成功反馈"""
        album = AlbumManagePage(page)
        album.enter_album_page()
        album.open_upload_popup()
        album.wait_tips(album.upload_tip)
        assert "上传成功" in album.get_text(album.upload_tip), "提示文案应为上传成功"
