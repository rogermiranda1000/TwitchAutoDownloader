from typing import Dict,Any
from time import sleep
import logging
import os
from .TwitchDownloaderFactory import TwitchDownloaderFactory
from ..VideoDownloader import VideoDownloader,InvalidQualityException
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
        # there's a bug with TwitchDl where sometimes the quality disappears, and another where the program crashes and it needs to be launched again; we'll try some times
        tries = 0
        max_tries = 4
        while tries < max_tries:
            try:
                self._twitchdl_downloader.download(id_or_url, quality, out_path)
                if not os.path.isfile(out_path):
                    raise Exception("Couldn't find file at its expected path.")
                break # downloaded succesfully
            except InvalidQualityException as ex: # retrying with other exceptions could be bad
                tries += 1
                if tries >= max_tries:
                    raise ex # reached max retries
                else:
                    # try again after some time
                    logging.debug("Got an " + ex.__class__.__name__ + "; trying again to make sure it's not a false-negative.")
                    logging.debug(ex, exc_info=True)
                    sleep(8)

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