import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class HoughCircleDetector:
	'''Detect circles in images using OpenCV's HoughCircles. This is an attempt at a literal implementation of the detector described in the J. Tollefson et.al. paper.'''

	SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

	def __init__(self, circle_params: Dict[str, Any], margin: float = 0.2) -> None:
		if margin < 0:
			raise ValueError("Margin must be non-negative.")
		required_params = {'dp', 'minDist', 'param1', 'param2', 'minRadius', 'maxRadius'}
		missing = required_params - circle_params.keys()
		if missing:
			raise ValueError(f"Missing required circle parameters: {missing}")

		self.circle_params = circle_params
		self.margin = margin

	def detect_circles(self, image: np.ndarray) -> Optional[np.ndarray]:
		'''Detect circles using the HoughCircles method.'''
		if len(image.shape) != 2:
			raise ValueError("Input image must be a grayscale image.")
		return cv2.HoughCircles(
			image,
			cv2.HOUGH_GRADIENT,
			dp=self.circle_params['dp'],
			minDist=self.circle_params['minDist'],
			param1=self.circle_params['param1'],
			param2=self.circle_params['param2'],
			minRadius=self.circle_params['minRadius'],
			maxRadius=self.circle_params['maxRadius']
		)

	def save_image(self, image: np.ndarray, path: Path) -> None:
		try:
			if not cv2.imwrite(str(path), image):
				logging.error(f"Failed to save image to {path}")
		except Exception as e:
			logging.error(f"Error saving image to {path}: {e}")

	def crop_circle(self, image: np.ndarray, x: int, y: int, r: int) -> np.ndarray:
		"""Crop a circle from an image with margin."""
		margin = int(self.margin * r)
		x1 = max(0, x - r - margin)
		y1 = max(0, y - r - margin)
		x2 = min(image.shape[1], x + r + margin)
		y2 = min(image.shape[0], y + r + margin)
		return image[y1:y2, x1:x2]

	def process_image(self, image_path: Path, positive_folder: Path, negative_folder: Path) -> None:
		try:
			image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
			if image is None:
				raise FileNotFoundError(f"Unable to read image: {image_path}")

			circles = self.detect_circles(image)
			if circles is not None:
				for i, (x, y, r) in enumerate(np.round(circles[0, :]).astype('int')):
					cropped = self.crop_circle(image, x, y, r)
					self.save_image(cropped, positive_folder / f"{image_path.stem}_circle_{i}.png")
			else:
				self.save_image(image, negative_folder / image_path.name)
		except Exception as e:
			logging.error(f"Error processing image {image_path}: {e}")

	def process_images_in_folder(self, input_folder: Path, positive_folder: Path, negative_folder: Path) -> None:
		positive_folder.mkdir(parents=True, exist_ok=True)
		negative_folder.mkdir(parents=True, exist_ok=True)

		image_files = [file for file in input_folder.rglob("*") if file.suffix.lower() in self.SUPPORTED_EXTENSIONS]
		total_files = len(image_files)

		def process_file(file: Path):
			self.process_image(file, positive_folder, negative_folder)
			logging.info(f"Processed {file.name}")

		with ThreadPoolExecutor() as executor:
			executor.map(process_file, image_files)

		logging.info(f"Processed {total_files} images in total.")
