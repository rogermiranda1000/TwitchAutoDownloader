from typing import Dict,Any
from .TwitchDownloaderFactory import TwitchDownloaderFactory
from ..VideoDownloader import VideoDownloader
from ..chat.ChatDownloader import ChatDownloader
from ..video.TwitchDlDownloader import TwitchDlDownloader

class VideoAndChatDownloader(VideoDownloader):
    """
    Merges ChatDownloader and TwitchDlDownloader to get both chat and video
    """
    def __init__(self, twitchdl_downloader: TwitchDlDownloader, chat_downloader: ChatDownloader):
        self._twitchdl_downloader = twitchdl_downloader
        self._chat_downloader = chat_downloader

    def download(self, id_or_url: str, quality: str, out_path: str):
        self._twitchdl_downloader.download(id_or_url, quality, out_path)

    def get_info(self, id_or_url: str) -> Dict[str,Any]:
        return self._twitchdl_downloader.get_info(id_or_url)

    def get_last_video(self, channel: str) -> str:
        return self._twitchdl_downloader.get_last_video(channel)

    def get_chat(self, id_or_url: str, format: str, out_path: str):
        self._chat_downloader.get_chat(id_or_url, format, out_path)

class TwitchVideoAndChatDownloaderFactory(TwitchDownloaderFactory):
    def build(self) -> VideoDownloader:
        return VideoAndChatDownloader(twitchdl_downloader=TwitchDlDownloader(),
                                      chat_downloader=ChatDownloader())