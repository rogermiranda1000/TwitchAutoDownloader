import json
import os
from typing import Dict,Any

class ConfigProvider:
    @property
    def download_while_stream(self) -> bool:
        pass

    @property
    def check_interval(self) -> float:
        pass

    @property
    def channel_name(self) -> str:
        pass

    @property
    def download_quality(self) -> str:
        pass

    @property
    def chat_format(self) -> str:
        pass

class JsonConfig(ConfigProvider):
    def __init__(self, path: str):
        self._configPath = path
        self._data = None

    @staticmethod
    def _get_defaults() -> Dict[str, Any]:
        return {
            'download_while_stream': True,  # to prevent sound loss (due to copyright)
            'check_interval': 6*60.0,       # 6 minute interval.
                                            # The max audio loss will be 2 times this number; check `TwitchDownloader._download` for explanation.
            'channel_name': '',             # where to download the videos
            'download_quality': '480p',     # downloaded video resolution
            'chat_format': 'srt'            # downloaded chat format
        }

    def create(self):
        with open(self._configPath, 'w') as f:
            json.dump(JsonConfig._get_defaults(), f, indent=2)

    def read(self, create_if_not_exists = True):
        if create_if_not_exists and not os.path.exists(self._configPath):
            print("[v] Couldn't find config file; creating it...")
            self.create()

        with open(self._configPath, 'r') as f:
            self._data = json.load(f)

    @property
    def loaded(self) -> bool:
        return self._data is not None

    @property
    def download_while_stream(self) -> bool:
        return self._data['download_while_stream']

    @property
    def check_interval(self) -> float:
        return self._data['check_interval']

    @property
    def channel_name(self) -> str:
        return self._data['channel_name']

    @property
    def download_quality(self) -> str:
        return self._data['download_quality']

    @property
    def chat_format(self) -> str:
        return self._data['chat_format']