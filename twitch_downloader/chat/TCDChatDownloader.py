from .ChatDownloader import ChatDownloader
from ..VideoDownloader import VideoDownloader

import os,shutil
import subprocess
import sys
from typing import List

class TCDChatDownloader(ChatDownloader):
    def __init__(self, tcd_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Twitch-Chat-Downloader/app.py")):
        self._interpreter = sys.executable
        self._tcd_path = tcd_path
        self._out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats')

    def get_chat(self, id_or_url: str, format: str, out_path: str):
        id = VideoDownloader.get_id(id_or_url)
        result = self._run_command(id, '--format', format)
        logging.debug(f"Result of the download chat command: ```{result}```")

        # move the file
        shutil.move(os.path.join(self._out_path, f'v{id}.srt'), out_path)

    def _run_command(self, *args: List[str]) -> str:
        result = subprocess.run([self._interpreter, '-u', self._tcd_path, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return result.stdout.decode('utf-8')