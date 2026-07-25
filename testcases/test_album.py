from page_objects.album_page import AlbumManagePage

class TestAlbumWeb:
    def test_album_batch_delete(self, page):
        """完整流程：进入相册→搜索相册→批量删除"""
        album = AlbumManagePage(page)
        album.enter_album_page()
        album.search_album_name("日常照片")
        album.batch_delete_album()