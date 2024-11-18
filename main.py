from scripts.hough_circle_detector import HoughCircleDetector
from scripts.contour_circle_detector import ContourCircleDetector

def main():
    # Paths for input and output
    input_folder = './sanborn_images/'
    hough_output_positive_folder = './output/positive_samples/hough/'
    hough_output_negative_folder = './output/negative_samples/hough/'
    contour_output_positive_folder = './output/positive_samples/contour/'
    contour_output_negative_folder = './output/negative_samples/contour/'

    # Circle parameters
    min_radius = 15		# Minimum radius to be detected (pixels)
    max_radius = 130		# Maximum radius to be detected (pixels)

    # HoughCircle-method-specific parameters
    circle_params = {
        'dp': 1.2,		# Inverse ratio of accumulator resolution to image resolution
        'minDist': 20,		# Minimum distance between detected centers (pixels)
        'param1': 220,		# Threshold for Canny edge detector
        'param2': 115,		# Accumulator threshold for circle centers
        'minRadius': min_radius,	
        'maxRadius': max_radius
    }

    hough_detector = HoughCircleDetector(circle_params)
    hough_detector.process_folder(input_folder, hough_output_positive_folder, hough_output_negative_folder)

    contour_detector = ContourCircleDetector(min_radius=min_radius, max_radius=max_radius)
    contour_detector.process_folder(input_folder, contour_output_positive_folder, contour_output_negative_folder)

    print("Pre-processing completed.")

if __name__ == '__main__':
    main()
