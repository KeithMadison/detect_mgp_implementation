
# Manufactured Gas Production (MGP) Site Semi-Automatic Labeler

## Overview

This repository provides a modular framework for performing the semi-automatic labeling Manufactured Gas Production (MGP) sites present in digitized Sanborn fire insurance maps. It combines image processing techniques and data scraping utilities, including:

- **Circle Detection:** Two complementary methods (Hough Transform and Contour Analysis) to detect circular shapes in images, useful for identifying specific map features.
- **Library of Congress Resource Scraper:** Automates downloading digital resources, filtering by MIME type, and organizing them for processing.
- **Pre-Processing Pipeline:** Integrates these tools for semi-automatic labeling, simplifying the identification of MGP sites from large datasets.

The pipeline's modularity makes it adaptable for various workflows beyond MGP site detection.

## Usage

`contour_circle_detector.py`: **Contour-Based Circle Detection Algorithm**

This script detects circles in images using contours and evaluates their circularity. It crops and saves detected circles or marks images with no circles.

##### Required Libraries

-   `opencv-python`
-   `numpy`
-   `concurrent.futures`
##### How to Use

1.  Instantiate the  `ContourCircleDetector`  class with the desired configuration:
    
```python
detector = ContourCircleDetector(
    min_radius=10,			# Minimum/maximum radius for detections
    max_radius=50,			
    min_circularity=0.85,	# Minimum/maximum circularity for classification as circle
    max_circularity=1.20
)
```

`hough_circle_detector.py`: **Hough-Transform-Based Circle Detection Algorithm**

This script uses OpenCV's `HoughCircles` method to detect circles in images, crop them, and save them to output folders. This is an attempt at a literal implementation of the procedure described in the J. Tollefson et. al. paper.

##### Required Libraries

-   `opencv-python`
-   `numpy`
-   `concurrent.futures`
##### How to Use

1.  Instantiate the `HoughCircleDetector` class with the [required parameters](https://docs.opencv.org/4.x/dd/d1a/group__imgproc__feature.html#ga47849c3be0d0406ad3ca45db65a25d2d):
    
```python
circle_params = {
    "dp": 1.2,
    "minDist": 20,
    "param1": 50,
    "param2": 30,
    "minRadius": 10,
    "maxRadius": 50
}
detector = HoughCircleDetector(circle_params)
```
    
2.  Process a folder of images:
    
```python
detector.process_images_in_folder(
    input_folder=Path("/path/to/images"),
    positive_folder=Path("/path/to/save/circles"),
    negative_folder=Path("/path/to/save/negatives")
)
```

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


<div style="color: black; background-color: yellow; padding: 10px; border-radius: 5px;">
⚠️ **Caution:** Proceed carefully.
</div>

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
