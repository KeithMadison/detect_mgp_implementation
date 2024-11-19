from components.hough_circle_detector import HoughCircleDetector
from components.contour_circle_detector import ContourCircleDetector
from components.library_of_congress_scraper import LibraryOfCongressResourceScraper
from pathlib import Path
import logging

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S",
)

def download_data() -> None:
	search_url = 'https://www.loc.gov/collections/sanborn-maps/?dates=1899/1899&fa=location:springfield'
	file_extension = '.jpg'
	save_to = './sanborn_images/'

	logging.info("Starting data download...")

	loc_scraper = LibraryOfCongressResourceScraper(search_url, file_extension, save_to)
	loc_scraper.download_files()

	logging.info("Data download completed.")

def prepare_output_directories(base_output='./output/'):
	output_dirs = {
		'hough_positive': Path(base_output, 'positive_samples', 'hough'),
		'hough_negative': Path(base_output, 'negative_samples', 'hough'),
		'contour_positive': Path(base_output, 'positive_samples', 'contour'),
		'contour_negative': Path(base_output, 'negative_samples', 'contour'),
	}

	for key, path in output_dirs.items():
		path.mkdir(parents=True, exist_ok=True)
	return output_dirs

def main():
	try:
		download_data()

		output_dirs = prepare_output_directories()

		# Parameters for the Hough circle detector, determined to provide
		# satisfactory results via trial and error
		circle_params = {
			'dp': 1.2,
			'minDist': 20,
			'param1': 300,
			'param2': 140,
			'minRadius': 15,
			'maxRadius': 130,
		}

		hough_detector = HoughCircleDetector(circle_params)
		contour_detector = ContourCircleDetector(min_radius=15, max_radius=130)

		input_folder = Path('./sanborn_images/')
		logging.info("Starting Hough Circle Detection.")

		hough_detector.process_images_in_folder(
			input_folder,
			output_dirs['hough_positive'],
			output_dirs['hough_negative']
		)

		logging.info("Starting Contour Circle Detection.")

		contour_detector.process_images_in_folder(
			input_folder,
			output_dirs['contour_positive'],
			output_dirs['contour_negative']
		)

		logging.info("Pre-processing completed successfully.")

	except Exception as e:
		logging.error(f"An error occurred: {e}")
		raise

if __name__=="__main__":
	main()
