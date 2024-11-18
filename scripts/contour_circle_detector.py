import os
import cv2
import numpy as np
from typing import List, Tuple, Optional

class ContourCircleDetector:
    """
    A class to detect circles in images using contour detection and circularity metrics.
    """

    def __init__(self, min_radius: int = 15, max_radius: int = 130) -> None:
        """
        Initializes the CircleDetector with specified radius limits.

        Args:
            min_radius (int): Minimum radius of circles to detect.
            max_radius (int): Maximum radius of circles to detect.
        """
        self.min_radius = min_radius
        self.max_radius = max_radius

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Applies preprocessing steps to the image such as blurring and edge detection.

        Args:
            image (np.ndarray): Grayscale image to preprocess.

        Returns:
            np.ndarray: Edge-detected image.
        """
        # Apply Gaussian Blur to reduce noise
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        # Edge detection using Canny
        edged = cv2.Canny(blurred, 50, 150)
        return edged

    def detect_circles(self, edged_image: np.ndarray) -> List[Tuple[int, int, int]]:
        """
        Detects circles in the edge-detected image based on contours and circularity.

        Args:
            edged_image (np.ndarray): Edge-detected image.

        Returns:
            List[Tuple[int, int, int]]: A list of detected circles as (x, y, radius).
        """
        detected_circles = []

        # Find contours in the edged image
        contours, _ = cv2.findContours(edged_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Loop over the contours
        for cnt in contours:
            # Calculate contour area and perimeter
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)

            if perimeter == 0:
                continue  # Avoid division by zero

            # Calculate circularity
            circularity = 4 * np.pi * (area / (perimeter * perimeter))

            # Filter contours based on circularity and area
            if 0.85 < circularity <= 1.2:
                # Minimum enclosing circle
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                if self.min_radius <= radius <= self.max_radius:
                    detected_circles.append((int(x), int(y), int(radius)))

        return detected_circles

    def process_image(self, image_path: str, output_positive_folder: str, output_negative_folder: str) -> None:
        """
        Processes a single image: detects circles and saves positive or negative samples accordingly.

        Args:
            image_path (str): Path to the input image.
            output_positive_folder (str): Directory to save positive samples (images with circles).
            output_negative_folder (str): Directory to save negative samples (images without circles).
        """
        try:
            # Read the image in grayscale
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise FileNotFoundError(f"Unable to read image: {image_path}")

            # Preprocess the image
            edged_image = self.preprocess_image(image)

            # Detect circles
            detected_circles = self.detect_circles(edged_image)

            if detected_circles:
                # Save each detected circle as an image, 20% larger than the detected radius
                for i, (x, y, r) in enumerate(detected_circles):
                    margin = int(0.2 * r)
                    x1 = max(0, x - r - margin)
                    y1 = max(0, y - r - margin)
                    x2 = min(image.shape[1], x + r + margin)
                    y2 = min(image.shape[0], y + r + margin)

                    circle_crop = image[y1:y2, x1:x2]
                    filename = os.path.splitext(os.path.basename(image_path))[0]
                    output_path = os.path.join(output_positive_folder, f"{filename}_circle_{i}.png")
                    cv2.imwrite(output_path, circle_crop)
            else:
                # Save the full image as a negative sample if no circles are detected
                filename = os.path.basename(image_path)
                output_path = os.path.join(output_negative_folder, filename)
                cv2.imwrite(output_path, image)

        except Exception as e:
            print(f"Error processing image {image_path}: {e}")

    def process_folder(self, input_folder: str, output_positive_folder: str, output_negative_folder: str) -> None:
        """
        Processes all images in the specified input folder.

        Args:
            input_folder (str): Directory containing input images.
            output_positive_folder (str): Directory to save positive samples.
            output_negative_folder (str): Directory to save negative samples.
        """
        # Create output directories if they don't exist
        os.makedirs(output_positive_folder, exist_ok=True)
        os.makedirs(output_negative_folder, exist_ok=True)

        # Supported image extensions
        supported_extensions = ('.jpg', '.png', '.jpeg', '.bmp', '.tiff')

        # Process each image in the input folder
        for filename in os.listdir(input_folder):
            if filename.lower().endswith(supported_extensions):
                image_path = os.path.join(input_folder, filename)
                self.process_image(image_path, output_positive_folder, output_negative_folder)

def main() -> None:
    """
    Main function to execute the circle detection process.
    """
    # Paths for input and output
    input_folder = './sanborn_images/'
    output_positive_folder = './output/positive_samples/'
    output_negative_folder = './output/negative_samples/'

    # Initialize the CircleDetector with default radius limits
    detector = ContourCircleDetector(min_radius=15, max_radius=130)
    detector.process_folder(input_folder, output_positive_folder, output_negative_folder)

    print("Processing completed.")

if __name__ == '__main__':
    main()
