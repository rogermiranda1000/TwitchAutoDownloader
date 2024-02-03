# Twitch Auto Downloader - Services

In order to start the Twitch Downloader automatically you can use (in Linux) `twitch-downloader.service`.

Remember to change the paths according to your system. In Ubuntu you should place the services in `/lib/systemd/system/`, and then run `sudo systemctl enable <service>.service`.