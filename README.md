# Manufactured Gas Production (MGP) Site Semi-Automatic Labeler

## Overview
This repository contains tools for:
1. Detecting circular shapes in images using both **Hough Transform** and **Contour Analysis** methods.
2. Downloading image resources from the **Library of Congress** (LOC) using a customizable scraping utility.
3. A data pre-processing pipeline which combines the above to facilitate the semi-automatic labeling of manufactured gas production (MGP) sites present in digitized Sanborn fire insurance maps made available by the Library of Congress.

Each tool is modular, allowing flexibility in usage for diverse image processing and data collection workflows.

---

## Features

### **Circle Detection**
- **Hough Circle Detector**:
  - Implements OpenCV's `HoughCircles` to detect circular shapes.
  - Customizable detection parameters: resolution, edge thresholds, minimum/maximum radius, etc.
  - Saves detected circles with optional margins for cropping.
- **Contour Circle Detector**:
  - Uses contour analysis to find circular objects.
  - Filters by circularity and area thresholds.
  - Supports batch processing of images in directories.

### **LOC Image Downloader**
- Scrapes and downloads resources from the **Library of Congress API**.
- Filters files by specific MIME types (e.g., JPEG, TIFF, PDF).
- Handles paginated results and retries on failure using exponential backoff.
- Ensures organized storage with unique filenames and directory structure.

---

## Directory Structure

```
project/
│
├── components/                       # Core modules for circle detection and scraping
│   ├── hough_circle_detector.py      # Implements Hough Transform for circle detection
│   ├── contour_circle_detector.py    # Uses contour analysis for circle detection
│   ├── loc_scraper.py                # Scraper for Library of Congress resources
│
├── sanborn_images/                   # Subset of Sanborn images used for testing
│   ├── sanborn0...._...              
│       ├── ...._....-.....jpg        # Individual Sanborn image file
│
├── output/                           # Processed samples produced during pre-processing
│   ├── positive_samples/             # Samples identified as positive (potential MGP sites)
│   │   ├── hough/                    # Detected using Hough Circle Detector
│   │   ├── contour/                  # Detected using Contour Circle Detector
│   │
│   ├── negative_samples/             # Samples identified as negative (non-MGP sites)
│       ├── hough/                    # Processed using Hough Circle Detector
│       ├── contour/                  # Processed using Contour Circle Detector
│
├── main.py                           # Entry point for the MGP detection data pre-processing pipeline
├── README.md                         # Project documentation
└── requirements.txt                  # List of Python dependencies for the project
```

___

## Requirements
- **Python**: 3.7 or higher
- **Dependencies**:
  - `opencv-python`
  - `numpy`
  - `requests`
  - `tenacity`
  - `argparse`
  - `logging`

Install all dependencies using:
```bash
pip install -r requirements.txt
```

___

# How to Run

## Circle Detection

### Hough Circle Detector
This detector uses the Hough Transform to identify circular shapes. Run it as follows:
```bash
python hough_circle_detector.py --input_folder ./images --output_positive ./output/positive --output_negative ./output/negative --params ./params.json
```
**Explanation**:
- `--input_folder`: Path to the folder containing images to process.
- `--output_positive`: Folder to save cropped images containing detected circles.
- `--output_negative`: Folder to save full images where no circles are detected.
- `--params`: JSON file containing circle detection parameters.

**Example JSON Configuration**:
```json
{
    "dp": 1.5,
    "minDist": 20,
    "param1": 100,
    "param2": 30,
    "minRadius": 10,
    "maxRadius": 100
}
```

### Contour Circle Detector
This detector identifies circular shapes based on their geometric properties:
```bash
python contour_circle_detector.py --input_folder ./images --output_positive ./output/positive --output_negative ./output/negative
```
**Explanation**:
- ADD EXPLANATION

---

## LOC Image Downloader
This script downloads files from the Library of Congress based on search criteria:
```bash
python loc_scraper.py --search_url "https://www.loc.gov/search" --file_extension jpg --save_to ./downloads
```
**Explanation**:
- `--search_url`: API endpoint or LOC query to scrape resources.
- `--file_extension`: Desired file type (e.g., `jpg`, `png`, `pdf`).
- `--save_to`: Directory where files will be stored.
