import requests
import time
import logging
from tenacity import retry, wait_exponential, stop_after_attempt
from typing import List, Dict, Optional, Any
from pathlib import Path
from urllib.parse import urlparse
import uuid
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class LOCImageDownloader:
    """
    A class to download files from the Library of Congress based on a search query.

    Example:
        downloader = LOCImageDownloader(search_url, file_extension, save_to)
        downloader.run()
    """

    MIME_TYPE_MAP = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "tif": "image/tiff",
        "tiff": "image/tiff",
        "pdf": "application/pdf",
        "png": "image/png",
    }

    # Constants for default delays (magic numbers provided by LOC)
    DEFAULT_REQUEST_DELAY = 1  # seconds
    DEFAULT_DOWNLOAD_DELAY = 2  # seconds
    MAX_PAGES = 100  # Safeguard for pagination loops

    def __init__(
        self,
        search_url: str,
        file_extension: str,
        save_to: str,
        request_delay: int = DEFAULT_REQUEST_DELAY,
        download_delay: int = DEFAULT_DOWNLOAD_DELAY
    ):
        """
        Initialize the downloader with search URL, desired file extension, and save path.

        Args:
            search_url (str): The search URL to query the LOC API.
            file_extension (str): Desired file extension (e.g., 'jpg', 'pdf').
            save_to (str): Directory to save downloaded files.
            request_delay (int): Delay between API requests in seconds.
            download_delay (int): Delay between file downloads in seconds.

        Raises:
            ValueError: If the specified file extension is unsupported or the save directory cannot be created.
        """
        if not search_url.startswith("http"):
            raise ValueError("Invalid search_url. Must start with http or https.")

        self.search_url = search_url
        self.file_extension = file_extension.lower()
        self.mime_type = self.MIME_TYPE_MAP.get(self.file_extension)
        if not self.mime_type:
            raise ValueError(f"Unsupported file extension: {self.file_extension}")
        self.save_to = Path(save_to)
        try:
            self.save_to.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise ValueError(f"Could not create save directory '{save_to}': {e}")

        self.session = requests.Session()
        self.request_delay = request_delay
        self.download_delay = download_delay

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
    def fetch_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """
        Fetch JSON data from a given URL.

        Args:
            url (str): The URL to fetch data from.
            params (Optional[Dict[str, Any]]): Additional parameters for the request.

        Returns:
            Optional[Dict]: The JSON data as a dictionary, or None if an error occurs.
        """
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            if 'application/json' not in response.headers.get("Content-Type", ""):
                logging.warning(f"Unexpected Content-Type for {url}: {response.headers.get('Content-Type')}")
                return None
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}", exc_info=True)
            return None

    def get_item_ids(self) -> List[str]:
        """
        Retrieve item IDs from the LOC search URL.

        Returns:
            List[str]: A list of item IDs.
        """
        logging.info("Fetching item IDs from the Library of Congress...")
        item_ids = []
        url = self.search_url
        pages_processed = 0

        while url and pages_processed < self.MAX_PAGES:
            data = self.fetch_json(url, {"fo": "json", "c": 100, "at": "results,pagination"})
            if not data:
                break

            results = data.get("results", [])
            for result in results:
                if "item" in result.get("id", "") and "collection" not in result.get("original_format", []):
                    item_ids.append(result["id"])

            url = data.get("pagination", {}).get("next")  # Get the next page URL
            pages_processed += 1

            # Be kind to the server
            time.sleep(self.request_delay)

        logging.info(f"Found {len(item_ids)} items.")
        return item_ids

    def get_image_urls(self, item_ids: List[str]) -> List[Dict[str, str]]:
        """
        Retrieve URLs for files matching the specified file type.

        Args:
            item_ids (List[str]): A list of item IDs.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing file URLs and item IDs.
        """
        logging.info("Retrieving file URLs for the specified items...")
        file_urls = []

        for processed, item_url in enumerate(item_ids, start=1):
            try:
                data = self.fetch_json(item_url, {"fo": "json"})
                logging.info(f"Processing item {processed}/{len(item_ids)}...")
                if not data:
                    continue

                for resource in data.get("resources", []):
                    files = resource.get("files", [])
                    flattened_files = self.flatten_files(files)
                    for file_info in flattened_files:
                        if file_info.get("mimetype") == self.mime_type:
                            file_urls.append({"file_url": file_info["url"], "item_id": item_url})

                # Be kind to the server
                time.sleep(self.request_delay)
            except Exception as e:
                logging.error(f"Error processing item {item_url}: {e}", exc_info=True)
                continue

        logging.info(f"Found {len(file_urls)} matching files.")
        return file_urls

    @staticmethod
    def flatten_files(files: List[Any]) -> List[Dict]:
        """
        Flatten a nested list of files into a single list of dictionaries.

        Args:
            files (List[Any]): A potentially nested list of files.

        Returns:
            List[Dict]: A flattened list of file dictionaries.

        Raises:
            ValueError: If an unexpected file structure is encountered.
        """
        flattened = []

        def _flatten(items):
            for item in items:
                if isinstance(item, list):
                    _flatten(item)
                elif isinstance(item, dict):
                    flattened.append(item)
                else:
                    raise ValueError("Unexpected file structure.")

        _flatten(files)
        return flattened

    def download_files(self, file_urls: List[Dict[str, str]]) -> None:
        """
        Download files from the given URLs and save them to the specified directory.

        Args:
            file_urls (List[Dict[str, str]]): A list of dictionaries containing file URLs and item IDs.
        """
        logging.info("Downloading files...")
        failed_downloads = []

        for index, file_info in enumerate(file_urls, start=1):
            file_url = file_info["file_url"]
            item_id = file_info["item_id"].strip("/").split("/")[-1]
            save_path = self.save_to / item_id
            save_path.mkdir(parents=True, exist_ok=True)

            # Determine the filename
            parsed_url = urlparse(file_url)
            filename = Path(parsed_url.path).name
            if not filename:
                filename = f"file_{uuid.uuid4().hex}.{self.file_extension}"

            file_path = save_path / filename

            # Ensure unique filename
            if file_path.exists():
                unique_suffix = uuid.uuid4().hex
                file_path = save_path / f"{file_path.stem}_{unique_suffix}{file_path.suffix}"

            logging.info(f"[{index}/{len(file_urls)}] Downloading {file_url} as {file_path}...")

            # Download the file
            try:
                with self.session.get(file_url, stream=True, timeout=10) as response:
                    response.raise_for_status()
                    with open(file_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
            except requests.RequestException as e:
                logging.error(f"Error downloading {file_url}: {e}", exc_info=True)
                failed_downloads.append(file_url)
                continue  # Proceed to the next file

            # Be kind to the server
            time.sleep(self.download_delay)

        if failed_downloads:
            logging.error(f"Failed to download {len(failed_downloads)} files.")
            for url in failed_downloads:
                logging.error(f"Failed URL: {url}")

    def run(self) -> None:
        """
        Execute the downloader: fetch item IDs, retrieve file URLs, and download files.
        """
        item_ids = self.get_item_ids()
        if not item_ids:
            logging.error("No items found.")
            return

        file_urls = self.get_image_urls(item_ids)
        if not file_urls:
            logging.error("No matching files found.")
            return

        self.download_files(file_urls)
