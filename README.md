# Twitch Auto Downloader

## Dependencies

- Download Anaconda
- Create a new conda environment named "twitch": `conda create -n twitch python=3.9`, and then activate it with `conda activate twitch`
- Install `ffmpeg`: `apt-get install ffmpeg`
- Download the [latest twitch-dl realease](https://github.com/ihabunek/twitch-dl/releases/latest) and change its name and permissions: `cd twitch_downloader/video && mv <.pyz file> twitch-dl && chmod +x twitch-dl`
- Install twitch-dl dependencies: `python3 -m pip install typing-extensions httpcore[asyncio]`
- Clone [tcd](https://github.com/TheDrHax/Twitch-Chat-Downloader): `cd twitch_downloader/chat && git clone https://github.com/TheDrHax/Twitch-Chat-Downloader.git`
- Install tcd's requirements: `cd Twitch-Chat-Downloader && python3 -m pip install -r requirements.txt`