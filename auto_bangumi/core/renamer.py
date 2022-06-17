import logging
import re
from pathlib import PurePath, PureWindowsPath

from conf import settings
from core import DownloadClient
from parser import TitleParser

logger = logging.getLogger(__name__)


class Renamer:
    def __init__(self, download_client: DownloadClient):
        self.client = download_client
        self._renamer = TitleParser()
        self.recent_info = self.client.get_torrent_info()
        self.rename_count = 0
        self.torrent_count = len(self.recent_info)

    def print_result(self):
        if self.rename_count != 0:
            logger.info(f"Finished checking {self.torrent_count} files' name, renamed {self.rename_count} files.")
        logger.debug(f"Checked {self.torrent_count} files")

    def refresh(self):
        self.recent_info = self.client.get_torrent_info()

    def run(self):
        for i in range(0, self.torrent_count):
            info = self.recent_info[i]
            name = info.name
            torrent_hash = info.hash
            path_parts = PurePath(info.content_path).parts \
                if PurePath(info.content_path).name != info.content_path \
                else PureWindowsPath(info.content_path).parts
            path_name = path_parts[-1]
            try:
                season = int(re.search(r"\d", path_parts[-2]).group())
            except Exception as e:
                logger.debug(e)
                season = 1
            folder_name = path_parts[-3]
            try:
                new_name = self._renamer.download_parser(name, folder_name, season, settings.method)
                if path_name != new_name:
                    self.client.rename_torrent_file(torrent_hash, path_name, new_name)
                    self.rename_count += 1
                else:
                    continue
            except:
                logger.warning(f"{path_name} rename failed")
                logger.debug(f"origin: {name}")
                if settings.remove_bad_torrent:
                    self.client.delete_torrent(torrent_hash)
        self.print_result()


if __name__ == "__main__":
    from conf.const_dev import DEV_SETTINGS
    settings.init(DEV_SETTINGS)
    client = DownloadClient()
    rename = Renamer(client)
    rename.run()
