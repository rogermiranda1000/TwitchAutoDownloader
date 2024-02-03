import re
from typing import Any,Dict

class VideoDownloader:
    @staticmethod
    def get_id(id_or_url: str) -> str:
        id_pattern = re.compile(r'(^|(twitch.tv/videos/))(\d+)$')
        match = id_pattern.search(id_or_url)
        if not match:
            raise Exception('Invalid video ID')

        return match.group(3)

    @staticmethod
    def get_url(id: str) -> str:
        return f"https://www.twitch.tv/videos/{id}"

    def download(self, id_or_url: str, quality: str, out_path: str):
        """
        Downloads a Twitch video.
        :param id_or_url str:   ID or URL of the Twitch video to download
        :param quality str:     Target quality for the downloaded video
        :param out_path str:    Target path where to download
        """
        raise NotImplementedError(f"Cannot run download function on {self.__class__.__name__} instance")

    def get_info(self, id_or_url: str) -> Dict[str,Any]:
        """
        Queries information about a video.
        """
        raise NotImplementedError(f"Cannot run get_info function on {self.__class__.__name__} instance")

    def get_last_video(self, channel: str) -> str:
        """
        Requests the last video from a channel.
        """
        raise NotImplementedError(f"Cannot run get_last_video function on {self.__class__.__name__} instance")

    def get_chat(self, id_or_url: str, format: str, out_path: str):
        """
        Queries the chat messages.
        :param id_or_url str:   ID or URL of the Twitch video to download
        :param format str:      Chat standard
        :param out_path str:    Target path where to download
        """
        raise NotImplementedError(f"Cannot run get_chat function on {self.__class__.__name__} instance")