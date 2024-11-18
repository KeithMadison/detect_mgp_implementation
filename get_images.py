import requests
import time
import os
import re
from typing import List, Dict, Optional


class LOCImageDownloader:
    """
    A class to download images from the Library of Congress based on a search query.
    """

    def __init__(self, search_url: str, file_extension: str, save_to: str):
        """
        Initialize the downloader with search URL, desired file extension, and save path.

        Args:
            search_url (str): The search URL to query the LOC API.
            file_extension (str): The desired file extension (e.g., 'jpg', 'tiff', 'pdf').
            save_to (str): The directory where images will be saved.
        """
        self.search_url = search_url
        self.file_extension = file_extension.lower()
        self.save_to = save_to
        if not os.path.exists(self.save_to):
            os.makedirs(self.save_to)
        self.session = requests.Session()

    def get_item_ids(self, filter_func: Optional[callable] = None) -> List[str]:
        """
        Retrieve a list of item IDs from the LOC search URL.

        Args:
            filter_func (callable, optional): A function that takes a result dict and returns True if the item should be included.

        Returns:
            List[str]: A list of item URLs.
        """
        items = []
        self._get_item_ids_recursive(self.search_url, items, filter_func)
        return items

    def _get_item_ids_recursive(self, url: str, items: List[str], filter_func: Optional[callable] = None):
        """
        Recursive helper function to get item IDs from LOC search results.

        Args:
            url (str): The URL to fetch items from.
            items (List[str]): The list to append item URLs to.
            filter_func (callable, optional): A function that takes a result dict and returns True if the item should be included.
        """
        # Check that the query URL is not an item or resource link.
        exclude = ["loc.gov/item", "loc.gov/resource"]
        if any(excl in url for excl in exclude):
            raise ValueError(
                "Your URL points directly to an item or resource page (you can tell because 'item' "
                "or 'resource' is in the URL). Please use a search URL instead. For example, instead "
                "of 'https://www.loc.gov/item/2009581123/', try 'https://www.loc.gov/maps/?q=2009581123'."
            )

        # Request pages of 100 results at a time
        params = {"fo": "json", "c": 100, "at": "results,pagination"}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return

        # Check that the response contains JSON data
        if 'json' not in response.headers.get('Content-Type', ''):
            print(f"Unexpected content type: {response.headers.get('Content-Type')}")
            return

        data = response.json()
        results = data.get('results', [])
        for result in results:
            # Filter out anything that's a collection or web page
            original_format = result.get("original_format", [])
            filter_out = ("collection" in original_format) or \
                         ("web page" in original_format)
            if filter_func and not filter_func(result):
                filter_out = True
            if not filter_out:
                # Get the link to the item record
                item = result.get("id")
                if item and item.startswith("http://www.loc.gov/item"):
                    # Filter out links to Catalog or other platforms
                    items.append(item)

        # Continue to the next page if available
        next_url = data.get("pagination", {}).get("next")
        if next_url:
            time.sleep(1)  # Be polite and avoid hitting the server too hard
            self._get_item_ids_recursive(next_url, items, filter_func)

    def get_image_urls(self, item_ids: List[str]) -> List[Dict[str, str]]:
        """
        Retrieve a list of image URLs for the given item IDs.

        Args:
            item_ids (List[str]): A list of item URLs.

        Returns:
            List[Dict[str, str]]: A list of dictionaries with 'image_url' and 'item_id' keys.
        """
        print('Generating a list of files to download . . .')
        items = []

        # Standardize the mimetype
        mimetype = self.file_extension
        if mimetype == 'tif':
            mimetype = 'tiff'
        if mimetype == 'jpg':
            mimetype = 'jpeg'

        if mimetype == 'pdf':
            full_mimetype = 'application/' + mimetype
        else:
            full_mimetype = 'image/' + mimetype

        params = {"fo": "json"}

        for item_url in item_ids:
            try:
                response = self.session.get(item_url, params=params)
                if response.status_code == 429:
                    print('Too many requests to the API. Stopping early.')
                    break
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching item {item_url}: {e}")
                continue

            resources = data.get('resources', [])
            for resource in resources:
                resource_url = resource.get('url', '')
                files = resource.get('files', [])
                found_file = False

                # Flatten any nested lists in files
                flat_files = self._flatten_files(files)

                for file_info in flat_files:
                    mimetype_in_file = file_info.get('mimetype', '')
                    if mimetype_in_file == full_mimetype:
                        image_url = file_info.get('url')
                        if image_url:
                            items.append({
                                'image_url': image_url,
                                'item_id': item_url
                            })
                            found_file = True
                if not found_file:
                    print(f"Note: No {mimetype} files found in {resource_url}")

            # Pause between requests
            time.sleep(2)

        print(f"\nFound {len(item_ids)} items")
        print(f"Found {len(items)} files to download")
        return items

    @staticmethod
    def _flatten_files(files_list):
        """
        Flatten the nested files list.

        Args:
            files_list (List): A list that may contain nested lists of files.

        Returns:
            List[Dict]: A flat list of file dictionaries.
        """
        flat_list = []
        for item in files_list:
            if isinstance(item, dict):
                flat_list.append(item)
            elif isinstance(item, list):
                flat_list.extend(item)
            else:
                print(f"Unexpected item in files: {item}")
        return flat_list

    def download_images(self, image_urls: List[Dict[str, str]]):
        """
        Download images from the list of image URLs.

        Args:
            image_urls (List[Dict[str, str]]): A list of dictionaries with 'image_url' and 'item_id' keys.
        """
        for item in image_urls:
            image_url = item['image_url']
            item_id = item['item_id']
            print(f'Downloading: {image_url}')
            try:
                # Create a filename based on the last part of the URL or from IIIF URL
                # Create a folder based on the item ID
                id_prefix = item_id.strip('/').split('/')[-1]
                directory = os.path.join(self.save_to, id_prefix)
                os.makedirs(directory, exist_ok=True)

                # IIIF URLs (jpegs) need to be parsed in a special way
                if 'image-services/iiif' in image_url:
                    # Split the URL by "/"
                    url_parts = image_url.split('/')
                    # Find the section that begins with "service:"
                    regex = re.compile(r"service:.*")
                    pointer = list(filter(regex.match, url_parts))
                    if pointer:
                        # Split that section by ":"; the last part will be the filename
                        filename_part = pointer[0].split(':')[-1]
                    else:
                        filename_part = 'image'
                    # Get the file extension
                    ext = image_url.split('.')[-1]
                    filename = f"{filename_part}.{ext}"
                else:
                    filename = image_url.split('/')[-1]

                filepath = os.path.join(directory, filename)
                print(f'Saving as: {filepath}')
                # Request the image and write to path
                with self.session.get(image_url, stream=True) as response:
                    response.raise_for_status()
                    with open(filepath, 'wb') as fd:
                        for chunk in response.iter_content(chunk_size=8192):
                            fd.write(chunk)
            except requests.exceptions.RequestException as e:
                print(f"Error downloading {image_url}: {e}")
            except OSError as e:
                print(f"File system error: {e}")
            # Pause between downloads
            time.sleep(6)

    def run(self, filter_func: Optional[callable] = None):
        """
        Run the downloader to get item IDs, image URLs, and download images.

        Args:
            filter_func (callable, optional): A function that takes a result dict and returns True if the item should be included.
        """
        item_ids = self.get_item_ids(filter_func=filter_func)
        if not item_ids:
            print("No item IDs found.")
            return
        image_urls = self.get_image_urls(item_ids)
        if not image_urls:
            print("No image URLs found.")
            return
        self.download_images(image_urls)


if __name__ == "__main__":
    search_url = 'https://www.loc.gov/collections/sanborn-maps/?dates=1800/1899&fa=location:springfield'
    file_extension = 'jpg'
    save_to = './test_images/'

    downloader = LOCImageDownloader(search_url, file_extension, save_to)
    downloader.run()

