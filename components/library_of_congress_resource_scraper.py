from urllib.parse import urlparse
import requests
import logging
import mimetypes
import uuid
import time
from typing import List, Optional, Any
from pathlib import Path

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S"
)

class LibraryOfCongressResourceScraper:
	'''
	A scraper class for downloading files from the Library of Congress digital collections.
	Heavily modified from: (https://github.com/LibraryOfCongress/data-exploration/tree/master/loc.gov%20JSON%20API/maps)
	'''

	# These magic numbers are provided by the Library of Congress (https://guides.loc.gov/fire-insurance-maps/sanborn-downloading).
	# The server appears dislike other values.
	REQUEST_DELAY = 1	# seconds
	DOWNLOAD_DELAY = 2	# seconds
	RESULTS_PER_PAGE = 100	

	def __init__(
		     self,
		     search_path: str,
		     file_extension: str,
		     output_directory: Path
	):

		parsed_url = urlparse(search_url)
		if not all([parsed_url.scheme, parsed_url.netloc]):
			raise ValueError(f"Invalid URL: {search_url}")

		self.search_url = search_url

		# Determine MIME type for the provided file extension
		file_extension = file_extension.lower()
		mime_type, _ = mimetypes.guess_type(f"file{file_extension}")
		if not mime_type:
			raise ValueError(f"Unsupported file extension: {file_extension}")

		self.file_extension = file_extension
		self.mime_type = mime_type
		self.output_directory = Path(output_directory)

		try:
			self.output_directory.mkdir(parents=True, exist_ok=True)
		except OSError as e:
			raise ValueError(f"Could not create output directory '{output_directory}': {e}")

		self.session = requests.Session()

	def _load_json_from_url(self, endpoint_url: str, query_params: dict[str, Any] | None = None) -> dict | None:
		try:
			response = self.session.get(endpoint_url, params=query_params, timeout=10)
			response.raise_for_status()

			content_type = response.headers.get("Content-Type", "").lower()
			if 'application/json' not in content_type:
				logging.warning(
					f"Unexpected Content-Type for {endpoint_url}: {content_type}. "
					f"Response body: {response.text[:500]}..."
			)
        
			return response.json() 
        
		except requests.exceptions.JSONDecodeError:
			logging.error(
			f"Failed to decode JSON from {endpoint_url}. "
			f"Response body: {response.text[:500]}..."
			)
			return None

		except requests.RequestException as http_error:
			logging.error(f"HTTP request error while accessing {endpoint_url}: {http_error}")
			return None

	def _get_item_ids(self) -> List[str]:
		item_ids = []
		pages_processed = 0
		url = self.search_url

		while url:
			data = self._load_json_from_url(url, {"fo": "json", "c": self.RESULTS_PER_PAGE, "at": "results,pagination"})
			
			if not data:
				break

			results = data.get("results", [])
			for result in results:
				if "item" in result.get("id", "") and "collection" not in result.get("original_format", []):
					item_ids.append(result["id"])

			url = data.get("pagination", {}).get("next")
			pages_processed += 1

			time.sleep(self.REQUEST_DELAY)

		return item_ids

	def _get_item_urls(self, item_ids: List[str]) -> List[dict[str, str]]:
		file_urls = []

		for processed, item_url in enumerate(item_ids, start=1):
			try:
				json_data = self._load_json_from_url(item_url, {"fo": "json"})
				if not json_data:
					continue

				for resource in json_data.get("resources", []):
					files = resource.get("files", [])
					flattened_files = self._flatten_files(files)
					for file_info in flattened_files:
						if file_info.get("mimetype") == self.mime_type:
							file_urls.append({"file_url": file_info["url"], "item_id": item_url})

				time.sleep(self.REQUEST_DELAY)
			except Exception as e:
				logging.error(f"Error occurred while processing item {item_url}: {e}", exc_info=True)
				raise

		return file_urls

	@staticmethod
	def _flatten_files(files: List[Any]) -> List[dict]:
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

	@staticmethod
	def _create_unique_filename(file_url: str, file_extension: str, save_path: Path) -> Path:
		parsed_url = urlparse(file_url)
		filename = Path(parsed_url.path).name
        
		# Fallback to a default name if the URL path does not have a file name
		if not filename:
			filename = f"file_{uuid.uuid4().hex}{file_extension}"
        	
		file_path = save_path / filename
        
		if file_path.exists():
			unique_suffix = uuid.uuid4().hex
			file_path = file_path.with_stem(f"{file_path.stem}_{unique_suffix}")

		return file_path

	def download_files(self) -> None:
		item_ids = self._get_item_ids()
		if not item_ids:
			logging.error("No items found.")
			return

		file_urls = self._get_item_urls(item_ids)
		if not file_urls:
			logging.error("No matching files found.")
			return

		failed_downloads = []

		for index, file_info in enumerate(file_urls, start=1):
			file_url = file_info["file_url"]
			item_id = file_info["item_id"].strip("/").split("/")[-1]
			save_path = self.output_directory / item_id
			save_path.mkdir(parents=True, exist_ok=True)

			file_path = self._create_unique_filename(file_url, self.file_extension, save_path)

			logging.info(f"[{index}/{len(file_urls)}] Downloading {file_url} as {file_path}...")

			CHUNK_SIZE = 8192

			try:
				with self.session.get(file_url, stream=True, timeout=10) as response:
					response.raise_for_status()
					with open(file_path, "wb") as f:
						for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
							f.write(chunk)
			except requests.RequestException as e:
				logging.error(f"Error downloading {file_url}: {e}", exc_info=True)
				failed_downloads.append(file_url)
				continue

			time.sleep(self.DOWNLOAD_DELAY)

		if failed_downloads:
			logging.error(f"Failed to download {len(failed_downloads)} files.")
			for url in failed_downloads:
				logging.error(f"Failed URL: {url}")
