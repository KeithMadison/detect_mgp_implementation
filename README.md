# Manufactured Gas Production (MGP) Site Semi-Automatic Labeler

## Overview
This repository contains tools for:
1. Detecting circular shapes in images using both **Hough Transform** and **Contour Analysis** methods.
2. Downloading digital resources from the **Library of Congress** using a customizable scraping utility.
3. A data pre-processing pipeline which combines the above to facilitate the semi-automatic labeling of manufactured gas production (MGP) sites present in digitized Sanborn fire insurance maps made available by the Library of Congress.

The pipeline is designed to be modular, allowing flexibility in usage for diverse image processing and data collection workflows. Though I employ it here for use in the detection of MGP sites, its components are highly independent of the broader data pre-processing pipeline.

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

### **Library of Congress Resource Scraper**
- Scrapes and downloads resources from the **Library of Congress API**.
- Filters files by specific MIME types (e.g., JPEG, TIFF, PDF).
- Ensures organized storage with unique filenames and directory structure.

---

## Directory Structure

```
project/
│
├── components/                                     # Core modules for circle detection and scraping
│   ├── hough_circle_detector.py                    # Implements Hough Transform for circle detection
│   ├── contour_circle_detector.py                  # Uses contour analysis for circle detection
│   ├── library_of_congress_resource_scraper.py     # Scraper for Library of Congress resources
│
├── sanborn_images/                                 # Subset of Sanborn images used for testing
│   ├── sanborn0...._...
│       ├── ...._....-.....jpg                      # Individual Sanborn image file
│
├── output/                                         # Processed samples produced during pre-processing
│   ├── positive_samples/                           # Samples identified as positive (potential MGP sites)
│   │   ├── hough/                                  # Detected using Hough Circle Detector
│   │   ├── contour/                                # Detected using Contour Circle Detector
│   │
│   ├── negative_samples/                           # Samples identified as negative (non-MGP sites)
│       ├── hough/                                  # Processed using Hough Circle Detector
│       ├── contour/                                # Processed using Contour Circle Detector
│
├── main.py                                         # Entry point for the MGP detection data pre-processing pipeline
├── README.md                                       # Project documentation
└── requirements.txt                                # List of Python dependencies for the project
```

___

## Requirements
- **Python**: 3.10 or higher
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


## Design Considerations

Write a summary here. Some of these are obvious, but I will mention them here for completeness. 

###  1. **Documentation**

 

Good code is well-documented. Documentation comprises both an explicit accounting in the form of formal, external documentation (e.g., user guides and, in this case, README files) and inline comments that clarify intent, logic, and complex sections of the code for future maintainers. Well-documented is not synonymous with extensively documented, however, and oftentimes good code explains itself without the need for excessive comments or external documentation. I strived for this by adhering to the following:

  

1. **Explicit Types and Return Types:**
  Using strongly typed variables and annotating functions with explicit return types.

2. **Intuitive Variable and Function Names:**
  Choosing descriptive names that convey the purpose of the variable, function, or class.

3. **Explicit Error and Logging Messages:**
  Employing structured logging and writing detailed error messages that explain what went wrong, where, and (where possible) why.

  Take, for example, the following function. Despite having minimal documentation, it is immediately clear what this function accomplishes and how. The expressive function name, along with explicit argument and return types, obviates the need for a verbose docstring. Intuitive variable names (e.g., unique_suffix) further enhance clarity. Making use of such libraries as `pathlib` ensures that the code is expressive and clearly conveys intent:

  

```python

@staticmethod

def _create_unique_filename(file_url: str, file_extension: str, save_path: Path) -> Path:

parsed_url = urlparse(file_url)

filename = Path(parsed_url.path).name

# Fallback to a default name if the URL path does not have a file name

if not filename:

filename = f"file_{uuid.uuid4().hex}{file_extension}"

file_path = save_path / filename

if file_path.exists():

unique_suffix = uuid.uuid4().hex

file_path = file_path.with_stem(f"{file_path.stem}_{unique_suffix}")

  

return file_path

```

### 2. Modularity & Reusability

Good code is (more often than not) highly modular. Modular code is not only easier to understand and maintain, but also serves as the foundation for scalable and efficient collaborative development. I strove for modularity and reusability in writing this pre-processing pipeline, and achieved it by adhering to the Single Responsibility Principle. The components are loosely coupled, interacting only through well-defined interfaces:

- `main.py`: The script `main.py` orchestrates the data pipeline,  handling high-level workflows and interacting with the detection classes through their public APIs (`process_images_in_folder`) without requiring any knowledge of their internal workings. Adding a new detection method would only require creating a new class/module without altering existing components.
- `XXX_circle_detector.py`: The circle detection algorithms (`hough_circle_detector.py` and `contour_circle_detector.py`) encapsulate of functionality into classes, ensuring that each class can be independently developed, tested, and reused. While I employ it here for the detection of MGP sites, any folder of images could be passed to either of these algorithms independently of the data preprocessing pipeline. Both detection classes utilize  `ThreadPoolExecutor`  for parallel processing of images, abstracting concurrency management and making it reusable for different workflows.
-  `library_of_congress_resource_scraper.py`: The class used for scraping the Sanborn map digitizations is designed to facilitate the scraping of *any* resources from the Library of Congress digital collections.

*NOTE TO SELF: Should discuss adhering to SRP within classes and functions as well...* Minimize Code Duplication, etc.

### 3. Robustness & Reliability
1. **Robust Error Handling:**
2. **Comprehensive Coverage of Edge Cases:**
3. **Testing and Validation:**
