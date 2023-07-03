# Chaos Downloader

This tools is designed to deal with chaos api from projectdiscovery.io

## Installation

```
git clone https://github.com/ali-0x11/chaos-downloader/
cd chaos-downloader
pip3 install -r requirements.txt
```

## Usage

```
chmod +x ./chaos-downloader.py
./chaos-downloader.py
```

![alt text](https://github.com/ali-0x11/chaos-downloader/blob/main/info.jpg?raw=true)

## Features:

- extract the new subdomains
- dealing with chaos api with more filters.
- unzip folders after downloading.
- colleting all domains in one file.
- you can use httprobe or httpx after downloading.

## notes:

- This tool works on Linux only.
- The tool will not give you the new subdomains if you run it for the first time because the tool depend on the database to compare the subdomains.
- The tool will run httprobe or httpx on new subdomains
