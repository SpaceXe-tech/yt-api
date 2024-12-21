<h1 align="center">youtube-downloader</h1>
Download Youtube Videos in mp4, webm and mp3 formats.

# Pre-requisite

- [Python>=3.10](https://python.org)

# Installation

> [!NOTE]
> This guide assumes you're running on a *nix system.

1. Clone repo.

```sh
git clone https://github.com/Simatwa/youtube-downloader
cd youtube-downloader
```

2. Setup virtual environment and install requirements

```sh
pip install virtualenv
virtualenv venv
source venv/bin/activate
make install
```

Make the necessary changes to [.env.example](.env.example) file and rename it **.env**.

3. Start the server

```sh
make runserver
```

> [!TIP]
> To boost server performance by minimizing the load on it, it's recommended to setup a separate server for serving static contents _(audio and videos)_. To do so, you can simply execute the [static_server.py](static_server.py) file and then pass along the url of the static server to the API's configuration using key `static_server_url`

# Important links

## [How to extract PO Token](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#po-token-guide)