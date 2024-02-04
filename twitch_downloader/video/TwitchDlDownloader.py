from ..VideoDownloader import VideoDownloader,InvalidQualityException
from typing import Any,Dict,List
import os
import re
import subprocess
import logging
from datetime import datetime,timedelta

class TwitchDlDownloader(VideoDownloader):
    def __init__(self, twitchdl_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "twitch-dl")):
        self._twitchdl_path = twitchdl_path

    def _run_command(self, *args: List[str]) -> str:
        result = subprocess.run([self._twitchdl_path, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return result.stdout.decode('utf-8')

    def download(self, id_or_url: str, quality: str, out_path: str):
        id = VideoDownloader.get_id(id_or_url)
        result = self._run_command('download', id, '--quality', quality)
        logging.debug(f"Result of the download command: ```{result}```")
        result = TwitchDlDownloader._escape_ansi(result)

        invalid_quality_pattern = re.compile(r'Quality \'' + re.escape(quality) + r'\' not found. Available qualities are: (.+)')
        invalid_quality_match = invalid_quality_pattern.search(result)
        if invalid_quality_match:
            raise InvalidQualityException(valid_qualities=invalid_quality_match.group(1).split(', '))

        ok_pattern = re.compile(r'Downloaded: (.+\.mkv)')
        ok_match = ok_pattern.search(result)
        if not ok_match:
            raise Exception(result) # something wrong happened
            
        VideoDownloader.move_and_reformat(ok_match.group(1), out_path)

    @staticmethod
    def _escape_ansi(line: str):
        """
        Removes the color from the string.
        @author https://stackoverflow.com/a/38662876/9178470
        """
        ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', line)

    def get_info(self, id_or_url: str) -> Dict[str,Any]:
        r = {}

        id = VideoDownloader.get_id(id_or_url)
        info = self._run_command('info', id)
        logging.debug(f"Result of the info command: ```{info}```")

        info_pattern = re.compile(r'Published\s+(\d{4}-\d{2}-\d{2})\s*@\s*(\d{2}:\d{2}:\d{2})\s+Length:\s*(.*)')
        info_match = info_pattern.search(TwitchDlDownloader._escape_ansi(info))
        if info_match:
            r['published'] = datetime.strptime(info_match.group(1) + " " + info_match.group(2), '%Y-%m-%d %H:%M:%S')

            # examples of length:
            # 47 h 59 min
            # 3 h 14 min
            # 35 min 46 sec
            length_pattern = re.compile(r'(?:(\d+) h)?\s*(\d+) min')
            length_match = length_pattern.search(info_match.group(3))
            if length_match:
                r['length'] = timedelta(minutes=int(length_match.group(2)), hours=int("0" if len(length_match.group(1)) == 0 else length_match.group(1)))

        return r

    def get_last_video(self, channel: str) -> str:
        info = self._run_command('videos', channel, '--limit', '1')
        logging.debug(f"Result of the videos command: ```{info}```")

        info = TwitchDlDownloader._escape_ansi(info)
        if info == "No videos found\n":
            return None
        elif info == "Channel " + channel + " not found\n":
            raise Exception(info)
        else:
            info_pattern = re.compile(r'Video (\d+)')
            info_match = info_pattern.search(info)
            if not info_match:
                raise Exception(f"Couldn't match regex on output {info}")
            
            return info_match.group(1) # last video ID