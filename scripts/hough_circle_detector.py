import os
import cv2
import numpy as np
from typing import Optional, Dict

class HoughCircleDetector:
    """
    A class to detect circles in images using the HoughCircles method from OpenCV.
    """

    def __init__(self, circle_params: Dict[str, float]) -> None:
        """
        Initializes the CircleDetector with specified HoughCircles parameters.

        Args:
            circle_params (Dict[str, float]): Parameters for the cv2.HoughCircles method.
        """
        self.circle_params = circle_params

    def detect_circles(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detects circles in a grayscale image.

        Args:
            image (np.ndarray): Grayscale image in which to detect circles.

        Returns:
            Optional[np.ndarray]: Array of detected circles, or None if no circles are found.
        """
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

            # Detect circles in the image
            circles = self.detect_circles(image)

            if circles is not None:
                # Convert circle parameters (x, y, radius) to integers
                circles = np.round(circles[0, :]).astype('int')

                # Save each detected circle as an image, 20% larger than the detected radius
                for i, (x, y, r) in enumerate(circles):
                    margin = int(0.2 * r)
                    x1, y1 = max(0, x - r - margin), max(0, y - r - margin)
                    x2, y2 = min(image.shape[1], x + r + margin), min(image.shape[0], y + r + margin)

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

        # Process each image in the input folder
        for filename in os.listdir(input_folder):
            if filename.lower().endswith(('.jpg', '.png')):
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

    # HoughCircles parameters
    circle_params = {
        'dp': 1.2,           # Inverse ratio of the accumulator resolution to the image resolution
        'minDist': 20,       # Minimum distance between detected centers
        'param1': 220,       # Threshold for the Canny edge detector
        'param2': 115,       # Accumulator threshold for circle centers
        'minRadius': 15,     # Minimum radius to be detected
        'maxRadius': 130     # Maximum radius to be detected
    }

    detector = HoughCircleDetector(circle_params)
    detector.process_folder(input_folder, output_positive_folder, output_negative_folder)

    print("Processing completed.")

if __name__ == '__main__':
    main()
