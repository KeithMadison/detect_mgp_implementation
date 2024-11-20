
# Manufactured Gas Production (MGP) Site Semi-Automatic Labeler

## Overview

This repository provides a modular framework for the semi-automatic labeling of  **Manufactured Gas Production (MGP)**  sites present in digitized Sanborn fire insurance maps. These scripts are an attempt to both recreate and improve upon the pre-processing pipeline described in the research article *Feature Extraction and Machine Learning Techniques for Identifying Historic Urban Environmental Hazards: New Methods to Locate Lost Fossil Fuel Infrastructure in US Cities* by Tollefson, Frickel, and Restrepo.

**Key Features:**

-   **Circle Detection Algorithms:**
    -   **Hough Transform Method:**  Utilizes the Hough Transform to detect circular shapes in images (this is the technique used in the J. Tollefson et.al. paper).
    -   **Contour Analysis Method:**  Employs contour analysis to identify circles based on shape characteristics.
-   **Library of Congress Resource Scraper:**  Automates the downloading of digital resources made available online by the Library of Congress, filtering by file type, and organizing them for research or archival purposes.
-   **Pre-Processing Pipeline:**  Integrates all tools into a cohesive pipeline for semi-automatic labeling MGS site labeling.

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
-   [Design Considerations](#design-considerations)

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
│   └── negative_samples/                 # Samples identified as negative (non-MGP sites)
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

-   `opencv-python`
-   `numpy`
-   `requests`
-   `tenacity`
-   `argparse`
-   `logging`
-   `concurrent.futures`  (Standard Library)
-   `pathlib`  (Standard Library)
-   `uuid`  (Standard Library)

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
    
    **Note:**  Ensure that the  `search_url`  is a valid Library of Congress API endpoint returning JSON data.
    

### 2. Circle Detection Algorithms

#### Description

Both  `hough_circle_detector.py`  and  `contour_circle_detector.py`  detect circular features in images. Circular features are cropped to a uniform size and saved in a specified output directory, as are images containing no circular features.

#### 2.1. Hough Transform Circle Detector

**Usage:**

1.  **Configure Parameters (Optional):**
    
    FILL IN HERE> SEE: https://docs.opencv.org/4.x/dd/d1a/group__imgproc__feature.html#ga47849c3be0d0406ad3ca45db65a25d2d
    
2.  **Run the Script:**
    
    
    ```bash
    python components/hough_circle_detector.py \
      --input_folder data/sanborn_images \
      --positive_folder output/positive_samples/hough \
      --negative_folder output/negative_samples/hough
    ```
    

#### 2.2. Contour-Based Circle Detector

**Usage:**

1.  **Configure Parameters (Optional):**
    
    Adjust parameters  `min_radius`,  `max_radius`,  `min_circularity`, and  `max_circularity`  as needed.
    
2.  **Run the Script:**
    
    
    ```bash
    python components/contour_circle_detector.py \
      --input_folder data/sanborn_images \
      --positive_folder output/positive_samples/contour \
      --negative_folder output/negative_samples/contour
    ``` 
    

### 3. Main Pipeline Script

The  `main.py`  script orchestrates the pre-processing pipeline, combining scraping and circle detection to perform the semi-automatic labeling of MGS sites.

**Usage:**

```bash
Needs command line args
```
    

## Design Considerations

The design of this pipeline emphasizes clarity, modularity, and robustness. By adhering to best practices in documentation, modularity, and error handling, the code is both user-friendly and highly maintainable. The components are purposefully structured to work independently, facilitating reuse and adaptation in different workflows beyond the immediate scope of MGP site detection. I have categorized my most significant design considerations as follows. Some of these are obvious, however I will mention them here for completeness.

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

1. **Separation of Concerns:** The pipeline is divided into distinct modules, each responsible for a specific task:
	- `main.py`: The script `main.py` orchestrates the data pipeline,  handling high-level workflows and interacting with the detection classes through their public APIs (`process_images_in_folder`) without requiring any knowledge of their internal workings. Adding a new detection method would only require creating a new class/module without altering existing components.
	- `XXX_circle_detector.py`: The circle detection algorithms (`hough_circle_detector.py` and `contour_circle_detector.py`) encapsulate of functionality into classes, ensuring that each class can be independently developed, tested, and reused. While I employ it here for the detection of MGP sites, any folder of images could be passed to either of these algorithms independently of the data preprocessing pipeline. Both detection classes utilize  `ThreadPoolExecutor`  for parallel processing of images, abstracting concurrency management and making it reusable for different workflows.
	-  `library_of_congress_resource_scraper.py`: The class used for scraping the Sanborn map digitizations is designed to facilitate the scraping of *any* resources from the Library of Congress digital collections.
2. **Adherence to SRP within Classes and Functions:** Within each class and function, responsibilities are kept focused. Methods are designed to perform a single task, which simplifies testing and reduces code duplication. *Note to self: include explicit example here*

### 3. Robustness & Reliability
1. **Robust Error Handling:** I employed comprehensive error handling to manage various potential issues. Critical operations, such as creating directories or downloading files, include try-except blocks to handle OS-level or HTTP errors gracefully. Error logs include both error details and traceback information when appropriate, aiding in troubleshooting.
2. **Comprehensive Coverage of Edge Cases:** I anticipated and addressed common edge cases, including (but not limited to):
	- Invalid or missing URLs, where fallback or specific error messages guide corrective action.
	- Situations where API responses are malformed or lack the expected content type (application/json).
	- Scenarios where files already exist in the output directory, handled by appending unique suffixes to filenames.
	- Nested data structures returned by the Library of Congress API, flattened using recursive logic for consistent processing.
3. **Testing and Validation:** While formal unit tests are not yet included (due to time constraints), all code was written with the intent to facilitate ease of testing. Functions and classes are modular and self-contained, with clear input and output parameters, making them straightforward to test independently. Explicit type annotations further aid in isolating components for testing. By minimizing side effects and external dependencies, the codebase allows for mocking and stubbing techniques in future unit tests. Additionally, many methods (e.g, `_flatten_file`) are deterministic and could be easily validated using simple doctests or lightweight testing frameworks.
