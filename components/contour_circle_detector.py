import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S",
)


class ContourCircleDetector:
	'''A class to detect circles using contours and circularity metrics.'''

	SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

	def __init__(
		self,
		min_radius: int,
		max_radius: int,
		min_circularity: float = 0.85,
		max_circularity: float = 1.20,
		margin: float = 0.20,
		canny_thresholds: Tuple[int, int] = (50, 150),
	) -> None:
		'''
		Args:
			min_radius (int): Minimum radius of circles to detect.
			max_radius (int): Maximum radius of circles to detect.
			min_circularity (float): Minimum circularity value for a valid circle.
			max_circularity (float): Maximum circularity value for a valid circle.
			margin (float): Proportional margin to include around detected circles when cropping.
			canny_thresholds (Tuple[int, int]): Thresholds for Canny edge detection.
		'''
		if min_radius <= 0 or max_radius <= 0:
			raise ValueError("Radii must be positive integers.")
		if min_radius > max_radius:
			raise ValueError("min_radius cannot be greater than max_radius.")
		if min_circularity <= 0 or max_circularity <= 0:
			raise ValueError("Circularity values must be positive.")

		self.min_radius = min_radius
		self.max_radius = max_radius
		self.min_circularity = min_circularity
		self.max_circularity = max_circularity
		self.margin = margin
		self.canny_thresholds = canny_thresholds

	def preprocess_image(self, image: np.ndarray) -> np.ndarray:
		'''Apply Gaussian blur and Canny edge detection to reduce noise.'''
		blurred = cv2.GaussianBlur(image, (5, 5), 0)
		edges = cv2.Canny(blurred, *self.canny_thresholds)
		return edges

	def detect_circles(self, edges: np.ndarray) -> List[Tuple[int, int, int]]:
		detected_circles = []
		contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		for contour in contours:
			area = cv2.contourArea(contour)
			perimeter = cv2.arcLength(contour, True)

			if perimeter == 0:
				continue

			circularity = 4 * np.pi * (area / (perimeter**2))
			if self.min_circularity < circularity <= self.max_circularity:
				(x, y), radius = cv2.minEnclosingCircle(contour)
				if self.min_radius <= radius <= self.max_radius:
					detected_circles.append((int(x), int(y), int(radius)))

		return detected_circles

	def save_image(self, image: np.ndarray, path: Path) -> None:
		try:
			success = cv2.imwrite(str(path), image)
			if not success:
				logging.error(f"Failed to save image to {path}")
		except Exception as e:
			logging.error(f"Error saving image to {path}: {e}")

	def crop_and_save_circle(self, image: np.ndarray, circle: Tuple[int, int, int], output_folder: Path, filename: str, index: int) -> None:
		x, y, r = circle
		margin = int(self.margin * r)
		x1 = max(0, x - r - margin)
		y1 = max(0, y - r - margin)
		x2 = min(image.shape[1], x + r + margin)
		y2 = min(image.shape[0], y + r + margin)

		cropped_circle_image = image[y1:y2, x1:x2]
		output_path = output_folder / f"{filename}_circle_{index}.png"
		self.save_image(cropped_circle_image, output_path)

	def process_image(self, image_path: Path, output_positive_folder: Path, output_negative_folder: Path) -> None:
		try:
			image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
			if image is None:
				raise FileNotFoundError(f"Unable to read image: {image_path}")

			edges = self.preprocess_image(image)
			detected_circles = self.detect_circles(edges)

			if detected_circles:
				for i, circle in enumerate(detected_circles):
					self.crop_and_save_circle(image, circle, output_positive_folder, image_path.stem, i)
			else:
				self.save_image(image, output_negative_folder / image_path.name)

		except Exception as e:
			logging.error(f"Error processing image {image_path}: {e}", exc_info=True)

	def process_images_in_folder(self, input_folder: Path, output_positive_folder: Path, output_negative_folder: Path) -> None:
		output_positive_folder.mkdir(parents=True, exist_ok=True)
		output_negative_folder.mkdir(parents=True, exist_ok=True)

		image_files = [file for file in input_folder.rglob("*") if file.suffix.lower() in self.SUPPORTED_EXTENSIONS]
		total_files = len(image_files)

		def process_file(image_file: Path):
			self.process_image(image_file, output_positive_folder, output_negative_folder)
			logging.info(f"Processed {image_file.name}")

		with ThreadPoolExecutor() as executor:
			executor.map(process_file, image_files)

		logging.info(f"Processed {total_files} images in total.")
