# Manufactured Gas Production (MGS) Site Semi-Automatic Labeller

## Overview
This repository contains tools for:
1. Detecting circular shapes in images using both **Hough Transform** and **Contour Analysis** methods.
2. Downloading image resources from the **Library of Congress** (LOC) using a customizable scraping utility.

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
