import cv2
import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path
import logging
import argparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ContourCircleDetector:
    """
    A class to detect circles in images using contour detection and circularity metrics.
    """

    SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

    def __init__(
        self,
        min_radius: int,
        max_radius: int,
        min_circularity: float = 0.85,
        max_circularity: float = 1.20,
        margin: float = 0.20
    ) -> None:
        """
        Initializes the ContourCircleDetector with specified radius and circularity limits.

        Args:
            min_radius (int): Minimum radius of circles to detect.
            max_radius (int): Maximum radius of circles to detect.
            min_circularity (float): Minimum circularity for a contour to be considered a circle.
            max_circularity (float): Maximum circularity for a contour to be considered a circle.
            margin (float): Proportional margin to include around detected circles when cropping.
        """
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.min_circularity = min_circularity
        self.max_circularity = max_circularity
        self.margin = margin

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Applies preprocessing steps to the image (blurring and edge detection).

        Args:
            image (np.ndarray): Grayscale image to preprocess.

        Returns:
            np.ndarray: Edge-detected image.
        """
        # Apply Gaussian Blur to reduce noise
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        # Perform edge detection using Canny
        edges = cv2.Canny(blurred, 50, 150)
        return edges

    def detect_circles(self, edges: np.ndarray) -> List[Tuple[int, int, int]]:
        """
        Detects circles in the edge-detected image based on contours and circularity.

        Args:
            edges (np.ndarray): Edge-detected image.

        Returns:
            List[Tuple[int, int, int]]: A list of detected circles as (x, y, radius).
        """
        detected_circles = []

        # Find contours in the edged image
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Loop over the contours
        for contour in contours:
            # Calculate contour area and perimeter
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)

            if perimeter == 0:
                continue  # Avoid division by zero

            # Calculate circularity
            circularity = 4 * np.pi * (area / (perimeter * perimeter))

            # Filter contours based on circularity and area
            if self.min_circularity < circularity <= self.max_circularity:
                # Minimum enclosing circle
                (x, y), radius = cv2.minEnclosingCircle(contour)
                if self.min_radius <= radius <= self.max_radius:
                    detected_circles.append((int(x), int(y), int(radius)))

        return detected_circles

    def process_image(self, image_path: Path, output_positive_folder: Path, output_negative_folder: Path) -> None:
        """
        Processes a single image: detects circles and saves positive or negative samples accordingly.

        Args:
            image_path (Path): Path to the input image.
            output_positive_folder (Path): Directory to save positive samples (images with circles).
            output_negative_folder (Path): Directory to save negative samples (images without circles).
        """
        try:
            # Read the image in grayscale
            image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise FileNotFoundError(f"Unable to read image: {image_path}")

            # Preprocess the image
            edges = self.preprocess_image(image)

            # Detect circles
            detected_circles = self.detect_circles(edges)

            if detected_circles:
                # Save each detected circle as an image, with specified margin
                for i, (x, y, r) in enumerate(detected_circles):
                    margin = int(self.margin * r)
                    x1 = max(0, x - r - margin)
                    y1 = max(0, y - r - margin)
                    x2 = min(image.shape[1], x + r + margin)
                    y2 = min(image.shape[0], y + r + margin)

                    cropped_circle_image = image[y1:y2, x1:x2]
                    filename = image_path.stem
                    output_path = output_positive_folder / f"{filename}_circle_{i}.png"
                    success = cv2.imwrite(str(output_path), cropped_circle_image)
                    if not success:
                        logging.error(f"Failed to save image to {output_path}")
            else:
                # Save the full image as a negative sample if no circles are detected
                output_path = output_negative_folder / image_path.name
                success = cv2.imwrite(str(output_path), image)
                if not success:
                    logging.error(f"Failed to save image to {output_path}")

        except FileNotFoundError as e:
            logging.error(f"File not found: {image_path}")
        except cv2.error as e:
            logging.error(f"OpenCV error processing {image_path}: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"Unexpected error processing {image_path}: {e}", exc_info=True)

    def process_folder(self, input_folder: Path, output_positive_folder: Path, output_negative_folder: Path) -> None:
        """
        Processes all images in the specified input folder.

        Args:
            input_folder (Path): Directory containing input images.
            output_positive_folder (Path): Directory to save positive samples.
            output_negative_folder (Path): Directory to save negative samples.
        """
        # Create output directories if they don't exist
        output_positive_folder.mkdir(parents=True, exist_ok=True)
        output_negative_folder.mkdir(parents=True, exist_ok=True)

        # Traverse the directory tree
        image_files = list(input_folder.rglob("*"))
        total_files = len(image_files)
        processed_files = 0

        for image_file in image_files:
            if image_file.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                self.process_image(image_file, output_positive_folder, output_negative_folder)
                processed_files += 1
                logging.info(f"Processed {processed_files}/{total_files} images.")

        logging.info("Processing complete.")
