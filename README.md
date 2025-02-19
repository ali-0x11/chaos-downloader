# Chaos Downloader

Chaos Downloader is a command-line tool designed to interface with the [Chaos API](https://projectdiscovery.io) provided by ProjectDiscovery. It streamlines subdomain extraction, filtering, and post-processing, making it an effective asset for your domain enumeration workflow.

## Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/ali-0x11/chaos-downloader/
cd chaos-downloader
pip3 install -r requirements.txt
```

## Usage

Make the script executable and run the tool:

```bash
chmod +x ./chaos-downloader.py
./chaos-downloader.py
```

![Example Output](https://github.com/ali-0x11/chaos-downloader/blob/main/info.jpg?raw=true)

## Features

- **Subdomain Extraction:** Automatically identifies and extracts new subdomains from API responses.
- **Advanced Filtering:** Leverages enhanced filters when interacting with the Chaos API for precise data retrieval.
- **Automated Decompression:** Unzips downloaded folders automatically to streamline your workflow.
- **Domain Aggregation:** Consolidates all domains into a single file for easy management and further analysis.
- **Post-Processing Integration:** Supports tools like httprobe or httpx to further probe and analyze the discovered subdomains.

## Notes

- **Linux Only:** This tool is designed to operate on Linux systems.
- **Initial Run Behavior:** The tool may not display new subdomains on the first run due to its dependency on an existing database for comparisons.
- **Automated Post-Processing:** On detecting new subdomains, the tool will automatically execute httprobe or httpx for further verification.
