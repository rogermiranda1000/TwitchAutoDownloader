FROM python:3.8.5-slim-buster

WORKDIR /TwitchAutoDownloader
COPY . .

RUN apt-get update \
    && apt-get install -y ffmpeg
RUN python3 -m pip install typing-extensions httpcore[asyncio]
RUN cd "twitch_downloader/chat/Twitch-Chat-Downloader" \
    && python3 -m pip install -r requirements.txt

WORKDIR /TwitchAutoDownloader
CMD ["python3", "-u", "TwitchDownloader.py"]