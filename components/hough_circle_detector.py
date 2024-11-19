import cv2
import numpy as np
from typing import Optional, Dict, Any
from pathlib import Path
import logging
import argparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class HoughCircleDetector:
    """
    A class to detect circles in images using the HoughCircles method from OpenCV.
    """

    SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

    def __init__(self, circle_params: Dict[str, Any], margin: float = 0.2) -> None:
        """
        Initializes the HoughCircleDetector with specified HoughCircles parameters.

        Args:
            circle_params (Dict[str, Any]): Parameters for the cv2.HoughCircles method.
            margin (float): Proportional margin to include around detected circles when cropping.
        """
        required_params = {'dp', 'minDist', 'param1', 'param2', 'minRadius', 'maxRadius'}
        if not required_params.issubset(circle_params.keys()):
            missing = required_params - circle_params.keys()
            raise ValueError(f"Missing required circle parameters: {missing}")

        self.circle_params = circle_params
        self.margin = margin

    def detect_circles(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detects circles in a grayscale image.

        Args:
            image (np.ndarray): Grayscale image in which to detect circles.

        Returns:
            Optional[np.ndarray]: Array of detected circles, or None if no circles are found.
        """
        if len(image.shape) != 2:
            raise ValueError("Input image must be a grayscale image.")

        circles = cv2.HoughCircles(
            image,
            cv2.HOUGH_GRADIENT,
            dp=self.circle_params['dp'],
            minDist=self.circle_params['minDist'],
            param1=self.circle_params['param1'],
            param2=self.circle_params['param2'],
            minRadius=self.circle_params['minRadius'],
            maxRadius=self.circle_params['maxRadius']
        )
        return circles

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

            # Detect circles in the image
            circles = self.detect_circles(image)

            if circles is not None:
                # Convert circle parameters (x, y, radius) to integers
                circles = np.round(circles[0, :]).astype('int')

                # Save each detected circle as an image, with specified margin
                for i, (x, y, r) in enumerate(circles):
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
