from components.hough_circle_detector import HoughCircleDetector
from components.contour_circle_detector import ContourCircleDetector
from components.loc_image_downloader import LOCImageDownloader
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    # Download data from the LOC
    search_url = 'https://www.loc.gov/collections/sanborn-maps/?dates=1899/1899&fa=location:springfield'
    file_extension = 'jpg'
    save_to = './sanborn_images/'
    loc_scraper = LOCImageDownloader(search_url, file_extension, save_to)
    loc_scraper.run()

    # Paths for input and output
    input_folder = Path('./sanborn_images/')
    hough_output_positive_folder = Path('./output/positive_samples/hough/')
    hough_output_negative_folder = Path('./output/negative_samples/hough/')
    contour_output_positive_folder = Path('./output/positive_samples/contour/')
    contour_output_negative_folder = Path('./output/negative_samples/contour/')

    # Ensure output directories exist
    hough_output_positive_folder.mkdir(parents=True, exist_ok=True)
    hough_output_negative_folder.mkdir(parents=True, exist_ok=True)
    contour_output_positive_folder.mkdir(parents=True, exist_ok=True)
    contour_output_negative_folder.mkdir(parents=True, exist_ok=True)

    # Circle parameters
    min_radius = 15             # Minimum radius to be detected (pixels)
    max_radius = 130            # Maximum radius to be detected (pixels)

    # HoughCircle-method-specific parameters
    circle_params = {
        'dp': 1.2,              # Inverse ratio of accumulator resolution to image resolution
        'minDist': 20,          # Minimum distance between detected centers (pixels)
        'param1': 300,          # Threshold for Canny edge detector
        'param2': 140,          # Accumulator threshold for circle centers
        'minRadius': min_radius,
        'maxRadius': max_radius
    }

    # Initialize detectors
    hough_detector = HoughCircleDetector(circle_params)
    contour_detector = ContourCircleDetector(min_radius=min_radius, max_radius=max_radius)

    # Process images with Hough Circle Detector
    logging.info("Starting Hough Circle Detection.")
    hough_detector.process_folder(input_folder, hough_output_positive_folder, hough_output_negative_folder)

    # Process images with Contour Circle Detector
    logging.info("Starting Contour Circle Detection.")
    contour_detector.process_folder(input_folder, contour_output_positive_folder, contour_output_negative_folder)

    logging.info("Pre-processing completed.")

if __name__ == '__main__':
    main()
