# Manufactured Gas Production (MGP) Site Semi-Automatic Labeler

## Overview

This repository provides a modular framework for the semi-automatic labeling of  **Manufactured Gas Production (MGP)**  sites present in digitized Sanborn fire insurance maps. These scripts are an attempt to both recreate and improve upon the pre-processing pipeline described in the research article *Feature Extraction and Machine Learning Techniques for Identifying Historic Urban Environmental Hazards: New Methods to Locate Lost Fossil Fuel Infrastructure in US Cities* by Tollefson, Frickel, and Restrepo.

**Key Features:**

-   **Circle Detection Algorithms:**
    -   **Hough Transform Method:**  Utilizes the Hough Transform to detect circular shapes in images (this is the technique used in the J. Tollefson et al. paper).
    -   **Contour Analysis Method:**  Employs contour analysis to identify circles based on shape characteristics.
-   **Library of Congress Resource Scraper:**  Automates the downloading of digital resources made available online by the Library of Congress, filtering by file type, and organizing them for research or archival purposes.
-   **Pre-Processing Pipeline:**  Integrates all tools into a cohesive pipeline for semi-automatic labeling MGP site labeling.

The modularity of the pipeline makes it adaptable for various image processing and data scraping workflows beyond the scope of MGP site detection.

## Table of Contents

-   [Directory Structure](#directory-structure)
-   [Requirements](#requirements)
-   [Installation](#installation)
-   [Usage](#usage)
    -   [1. Library of Congress Resource Scraper](#1-library-of-congress-resource-scraper)
    -   [2. Circle Detection Algorithms](#2-circle-detection-algorithms)
        -   [2.1. Hough Transform Circle Detector](#21-hough-transform-circle-detector)
        -   [2.2. Contour-Based Circle Detector](#22-contour-based-circle-detector)
    -   [3. Main Pipeline Script](#3-main-pipeline-script)
-   [Results](#results)

## Directory Structure

```
project/
├── components/                           # Core modules for circle detection and scraping
│   ├── contour_circle_detector.py        # Contour-based circle detection
│   ├── hough_circle_detector.py          # Hough Transform circle detection
│   └── library_of_congress_scraper.py    # Scraper for Library of Congress resources
│
├── data/
│   └── sanborn_images/                   # Sanborn images used for processing
│       ├── image1.jpg
│       ├── image2.jpg
│       └── ...
│
├── output/                               # Processed samples produced during pre-processing
│   ├── positive_samples/                 # Samples identified as positive (potential MGP sites)
│   │   ├── hough/
│   │   └── contour/
│   └── negative_samples/                 # Samples identified as negative (maps containing no identified potential MGP sites)
│       ├── hough/
│       └── contour/
│
├── main.py                               # Entry point for the MGP semi-automaric labeling pipeline
├── README.md                             # Project documentation
├── requirements.txt                      # List of Python dependencies
```

## Requirements

-   **Python**: 3.10 or higher

### Python Dependencies

-   `opencv-python>=4.5.5`
-   `requests`
-   `numpy>=1.12`
-   `logging` (Standard Library)
-   `concurrent.futures`  (Standard Library)
-   `pathlib`  (Standard Library)
-   `uuid`  (Standard Library)
-   `argparse` (Standard Library)
-   `typing` (Standard Library)
-   `time` (Standard Library)
-   `mimetypes` (Standard Library)

## Installation

1.  **Clone the Repository:**

	```bash
	git clone https://github.com/yourusername/the-bccv-repo-name.git
    cd the-bccv-repo-name
	```
    
2.  **Create a Virtual Environment (Optional but Recommended):**
    
	```bash
	python3 -m venv venv
    source venv/bin/activate
	```
    
3.  **Install Dependencies:**
    
	```bash
	pip install -r requirements.txt
	```
    

## Usage

### 1. Library of Congress Resource Scraper

#### Description

The `library_of_congress_scraper.py` script automates the downloading of resources from the Library of Congress digital collections, allowing users to filter files by extension and save them locally for research or archival purposes. Usage is quite straightforward.

#### Example Usage

```python
search_url = 'https://www.loc.gov/collections/sanborn-maps/?dates=1899/1899&fa=location:springfield'
file_extension = '.jpg'
save_to = './output_directory/'

loc_scraper = LibraryOfCongressResourceScraper(search_url, file_extension, save_to)
```

**Note:** Ensure that the `search_url` is a valid Library of Congress API endpoint returning JSON data.
    

### 2. Circle Detection Algorithms

#### Description

Both  `hough_circle_detector.py`  and  `contour_circle_detector.py`  detect circular features in images. Circular features are cropped to a uniform size and saved in a specified output directory, as are images containing no circular features.

#### 2.1. Hough Transform Circle Detector

The `HoughCircleDetector` class makes use of OpenCV's HoughCircles in the automated detection of circular features in images contained in some specified directory. This is an attempt at a literal implementation of the detector described in the J. Tollefson et al. paper.

**Usage:**

1.  **Configure Parameters (Required):**
    
    OpenCV's HoughCircles requires the setting of a variety of detection parameters. You can read more about them in [the OpenCV documentation](https://docs.opencv.org/4.x/dd/d1a/group__imgproc__feature.html#ga47849c3be0d0406ad3ca45db65a25d2d).

    **Example:**

	```python
	circle_params = {
		'dp': 1.2,		# Inverse ratio of the accumulator resolution to the image resolution. Higher values mean lower resolution.
		'minDist': 20,		# Minimum distance between the centers of detected circles (pixels).
		'param1': 300,		# Higher threshold for the Canny edge detector (lower threshold is half of this value).
		'param2': 140,		# Accumulator threshold for the circle centers at the detection stage. Higher values detect fewer circles.
		'minRadius': 15,	# Minimum circle radius to be detected (pixels).
		'maxRadius': 130,	# Maximum circle radius to be detected (pixels).
	}
	```
    
2.  **Run the Detector:**
    
    
    ```python
    input_folder = Path('./input/')			# Directory containing images.
    positive_output_folder = Path('./positive/')	# Detected circular features, cropped from images.
    negative_output_folder = Path('./negative/')	# Images containing circles
    
    hough_detector = HoughCircleDetector(circle_params)
    hough_detector.process_images_in_folder(
                         input_folder,
                         positive_output_folder,
                         negative_output_folder
    )
    ```
    

#### 2.2. Contour-Based Circle Detector

The `ContourCircleDetector` class makes use of contours and circularity metrics to identify circular features in images. Circular features are cropped to a uniform size and saved in a specified output directory, as are images containing no circular features.

**Usage:**

1.  **Configure Parameters (Required):**

    The contour-based circle detector has comparatively few tunable parameters. The minimum and maximum circle radius to be detected must be set. The minimum and maximum circularities of a valid circle have default values of `0.85` and `1.20`, respectively, which works well in many cases. 

    **Example:**

	```python
	min_radius = 15		# Minimum circle radius to be detected (pixels).
 	max_radius = 130	# Maximum circle radius to be detected (pixels).
 	min_circularity = 0.85	# Minimum circularity value for a valid circle.
 	max_circularity = 1.20	# Maximum circularity value for a valid circle.
	```
    
2.  **Run the Detector:**
    
    
    ```python
    input_folder = Path('./input/')			# Directory containing images.
    positive_output_folder = Path('./positive/')	# Detected circular features, cropped from images.
    negative_output_folder = Path('./negative/')	# Images containing circles
    
    contour_detector = ContourCircleDetector(min_radius, max_radius)
    contour_detector.process_images_in_folder(
                         input_folder,
                         positive_output_folder,
                         negative_output_folder
    )
    ``` 
    

### 3. Main Pipeline Script

The  `main.py`  script orchestrates the pre-processing pipeline, combining scraping and circle detection to perform the semi-automatic labeling of MGP sites.

**Usage:**

```bash
python main.py --dates "1900/1901" --location "new-york" --sanborn_images "./sanborn_images_folder" --output "./preprocessing_output_folder"
```
    
## Results

I ran both the Contour and Hough algorithms on a subset of the Sanborn dataset consisting of 786 maps from the time period 1800 - 1899 and from the city of Springfield (chosen for no particular reason). I then visually inspected the output, and counted the number of true positives, true negatives, false positives, and false negatives. I define each term as follows:

- **Circular Feature:** I define a circular feature as any structure or demarcation in an image that is qualitatively precisely circular. This excludes items like pencil-drawn circles highlighting numbers, as well as characters such as "0" or "O." MGP sites are a subset of these circular features.
- **True Positive/Negative:** A true positive is a **cropped image** of a circular feature. A true negative is **a map** that was returned containing no identifiable circular features.
- **False Positive/Negative:** A false positive, accordingly, is a cropped image containing no identifiable circular feature. A false negative is a map which was returned and which contains at least one identifiable circular feature.
  
![Examples of true and false positives.](/assets/true_and_false_positive_examples.png)

Notice that these definitions differ from those used in the J. Tollefson et al. paper. The reasons are twofold: firstly, this pre-processing step is not intended to identify MGP sites; secondly, I was unable to identify a reasonably sized subset of the Sanborn dataset containing a sufficient number of identifiable MGP sites for meaningful evaluation.

The performance of the Contour and Hough methods were evaluated using standard classification metrics derived from their respective confusion matrices. These results highlight the differences in accuracy, precision, recall, and overall effectiveness between the two approaches. It should be noted that I am somewhat unfamiliar with the Hough algorithm, and it is quite possible that an improved parameter configuration should yield more promising results.

### Contour
The Contour method demonstrated a strong performance, with a higher proportion of correct classifications. The confusion matrix for this method is as follows:

|                | **True** | **False** |
|----------------|----------|-----------|
| **Positive**   | 116      | 48        |
| **Negative**   | 594      | 14        |

### Hough
The Hough method struggled with a significantly higher number of false positives and false negatives. Its confusion matrix is shown below:

|                | **True** | **False** |
|----------------|----------|-----------|
| **Positive**   | 33       | 212       |
| **Negative**   | 472      | 174       |

### Performance (Accuracy & Precision)

I define the following accuracy, precision, and performance metrics in the standard ways (see below for explicit formulae). Contour demonstrates superior performance across all metrics compared to Hough, achieving significantly higher accuracy (92% vs. 57%), which indicates its reliability for overall classification. With a precision of 71%, Contour effectively minimizes false positives, while Hough struggles at just 13%. In terms of recall, Contour excels at 89%, identifying the majority of true positives, whereas Hough’s recall of 16% highlights its poor sensitivity to positive cases. Combining these metrics, Contour achieves a robust F1 score of 0.79, showcasing its balanced performance, while Hough’s F1 score of 0.15 reflects significant challenges in maintaining this balance. Making any conclusions about their respective performance, however, would require further tuning of parameters, and perhaps sensitivity analyses for various parameters:

| Metric      | Contour  | Hough    |
|-------------|----------|----------|
| Accuracy    | 0.92     | 0.57     |
| Precision   | 0.71     | 0.13     |
| Recall      | 0.89     | 0.16     |
| F1 Score    | 0.79     | 0.15     |

### Formulae:
 - $\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{TP} + \text{FP} + \text{TN} + \text{FN}}$
 - $\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$
 - $\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$
 - $\text{F1 Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$
