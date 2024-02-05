#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import logging
import time
import shutil
import tempfile
import signal
import sys
from pathlib import Path
from datetime import datetime,timedelta
from enum import Enum
from config.ConfigManager import JsonConfig,ConfigProvider
from twitch_downloader.VideoDownloader import VideoDownloader
from twitch_downloader.factory.TwitchDownloaderFactory import TwitchDownloaderFactory
from twitch_downloader.factory.TwitchVideoAndChatDownloaderFactory import TwitchVideoAndChatDownloaderFactory

class TwitchDownloader:
    class TwitchDownloaderState(Enum):
        WAITING_FOR_VIDEO = 1
        CAPTURING = 2

    def __init__(self, config: ConfigProvider, video_downloader_factory: VideoDownloader):
        self._config = config
        self._video_downloader = video_downloader_factory.build()
        self._tmp_dir = str(tempfile.TemporaryDirectory())
        self._start = False

        self._videos_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
        Path(self._videos_folder).mkdir(parents=True, exist_ok=True)

    def _download(self, id: str, tmp: bool = False):
        # If we're capturing a temporal video, we must store the last 3 videos. Explanation:
        # Let's assume we're capturing a video and we store it as "A.mp4"
        # Then, we'll trigger another download 1 second before the video ends, this is "B.mp4"
        # and as the download will last more than 1 second it is invalid, because there's a
        # potential data loss.
        # Finally, as the download was started before it ended we'll trigger this function
        # one last time, downloading "C.mp4".
        # In the next tick the program will realize that C.mp4 is the complete stream, and will
        # merge it (if enabled) with the uncompleted one. In this case, we want to pick "A.mp4".

        target_path = os.path.join(self._videos_folder, id + ".mkv") # TODO mp4
        tmp_target_path_gen = lambda n : os.path.join(self._tmp_dir, id + "." + str(n) + ".mkv") # mkv extension requires less operations
        if tmp:
            # move "B" and "C" (if they exist)
            shutil.move(tmp_target_path_gen(2), tmp_target_path_gen(1))
            shutil.move(tmp_target_path_gen(3), tmp_target_path_gen(2))
            # we're writting on "C"
            target_path = tmp_target_path_gen(3)
        else:
            # if we got "C", then we can export it directly
            if os.path.isfile(tmp_target_path_gen(3)):
                logging.debug("Re-using latest tmp video.")
                VideoDownloader.move_and_reformat(tmp_target_path_gen(3), target_path)
                return # we got it
            # we weren't downloading tmp files; download the final video

        self._video_downloader.download(id, self._config.download_quality, target_path)


    def _merge(self, id: str):
        target_path = os.path.join(self._videos_folder, id + ".mkv") # TODO mp4
        tmp_target_path_gen = lambda n : os.path.join(self._tmp_dir, id + "." + str(n) + ".mkv")
        to_merge = tmp_target_path_gen(1)

        if not os.path.isfile(to_merge):
            logging.debug("Nothing to merge.")
            return

        logging.debug(f"Merging '{to_merge}' with '{target_path}'...")
        # TODO merge instead of this
        VideoDownloader.move_and_reformat(to_merge, os.path.join(self._videos_folder, "start_" + id + ".mkv"))

    def __tick(self):
        if self._state == TwitchDownloader.TwitchDownloaderState.WAITING_FOR_VIDEO:
            # is the next video already there?
            last_id = self._video_downloader.get_last_video(self._config.channel_name)
            last_id_info = None if last_id is None else self._video_downloader.get_info(last_id)
            if last_id is not None:
                if self._last_time < last_id_info['published']:
                    # new video found
                    logging.info("Found a new video! Starting to capture...")
                    self._current_video = last_id
                    self._current_video_duration = timedelta(0) # simulate that we've captured this video when it was 0 seconds long
                    self._state = TwitchDownloader.TwitchDownloaderState.CAPTURING

                    # as now we've changed the stage, capture what we've already got
                    self.__tick()
                else:
                    logging.debug("No new video got.")
        elif self._state == TwitchDownloader.TwitchDownloaderState.CAPTURING:
            current_video_info = self._video_downloader.get_info(self._current_video)
            if self._current_video_duration < current_video_info['length']:
                # got new data
                logging.debug(f"The stream is still going.")
                
                if self._config.download_while_stream:
                    self._download(self._current_video, tmp=True)
                    logging.debug(f"Overriden latest video for the new one.")
                    
                self._current_video_duration = current_video_info['length'] # update the current downloaded length
            else:
                # the video has ended
                logging.info("The video has ended.")

                self._download(self._current_video)
                if self._config.download_while_stream:
                    # we have old videos pending to merge
                    self._merge(self._current_video)

                self._current_video = None
                self._current_video_duration = None
                self._last_time = last_id_info['published'] # update the "last download video" time
                self._state = TwitchDownloader.TwitchDownloaderState.WAITING_FOR_VIDEO
        else:
            logging.warning(f"Got a tick while having unknown stage: {self._state}")

    async def run(self):
        if self.started:
            raise Exception("Can't run the same instance twice!")

        self._start = True
        self._state = TwitchDownloader.TwitchDownloaderState.WAITING_FOR_VIDEO
        if not self._config.loaded:
            self._config.read()

        # check latest video
        # We'll use time instead of ID comparison just in case a video gets deleted;
        # if the "latest video" is before `_last_time`, then there's no new video.
        try:
            last_id = self._video_downloader.get_last_video(self._config.channel_name)
            self._last_time = datetime.min
            self._current_video = None
            self._current_video_duration = None
            if last_id is not None:
                self._last_time = self._video_downloader.get_info(last_id)['published']
        except Exception as ex:
            # even if there's no video we shouldn't expect an expection; crashing means something really bad happened
            logging.critical(ex, exc_info=True)
            self.stop()

        # check&download loop
        while self.started:
            start_time = time.time()
            try:
                self.__tick()
            except Exception as ex:
                logging.error(ex, exc_info=True)
            end_time = time.time()

            # wait for the next petition
            try:
                sleep_for = self._config.check_interval - (end_time - start_time)
                if sleep_for > 0:
                    logging.debug(f"Sleeping for {sleep_for:.1f} seconds")
                    await asyncio.sleep(sleep_for)
            except Exception as ex:
                # as this is high severity (if we don't run the sleep in a loop it will cause a lot of petitions), we'll stop the program
                logging.critical(ex, exc_info=True)
                self.stop()

    @property
    def started(self) -> bool:
        return self._start

    def stop(self):
        self._start = False
        self._tmp_dir.cleanup()


async def main():
    global downloader
    config = JsonConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"))

    # TODO forward logger msg to Discord
    # logger = logging.getLogger('shrubbery')
    # create a class inheriting `logging.Filter`
    # logger.addFilter(f)

    video_downloader_factory = TwitchVideoAndChatDownloaderFactory()
    downloader = TwitchDownloader(config, video_downloader_factory)

    await downloader.run()

def signal_handler(sig, frame):
    global downloader
    print('Got SIGINT; cleaning...')
    downloader.stop()
    sys.exit(0) # TODO abort sleep instead of exiting

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    signal.signal(signal.SIGINT, signal_handler)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())