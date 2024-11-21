# Summary & Review of J. Tollefson et al. Paper

Background

The J. Tollefson et al. paper addresses the challenge of locating undocumented manufactured gas plant (MGP) sites present in urban environments. These sites, active during the 19th and early 20th centuries, represent significant environmental hazards, but are largely absent from modern records. Traditional methods for identifying these sites (such as manual map inspection) are labor-intensive and inefficient. The solution proposed in this paper makes use of digitized Sanborn fire insurance maps (hosted by the Library of Congress) and a two-step machine learning pipeline to locate MGP sites. 

Methodology

The authors propose an automated pipeline (“Detect_MGP”), which uses machine learning techniques to identify potential MGP sites in digitized Sanborn fire insurance maps. The process involves:

1. Data Preprocessing:
    1. Sanborn fire insurance maps are scraped from the Library of Congress’ digital catalogue.
    * Circular structures (a common feature of MGP sites) are identified in these maps using the Hough Transform. Candidate regions are extracted from them, and are resized and standardized for further processing.
    * These regions are resized and standardized for further processing.
2. Machine Learning Classification:
    * An ensemble model combining five convolutional neural networks (CNNs) and five multilayer perceptrons (MLPs) classifies the candidate regions as MGP or non-MGP.
    * CNNs are used for feature extraction from images, leveraging their ability to preserve spatial relationships and handle translation invariance.
    * MLPs complement CNNs by providing a lightweight classification approach, contributing to ensemble accuracy with minimal computational overhead.
3. Ensemble Prediction:
    * Predictions from the CNN and MLP models are averaged and adjusted using optimized thresholds for final classification.
4. Post-processing and Validation:
    * The method aggregates circular regions back to full map pages for manual verification, achieving an overall recall rate of ~90%.
    * 
The pipeline significantly reduces the time required for manual map inspection, enhancing scalability for historical environmental hazard research.

Results 

The pipeline was evaluated using a dataset of 16,393 digitized Sanborn map pages:

1. Reduction in Manual Effort:
    * The pipeline reduced the time required for Sanborn map page assessment by 94%. For example, analyzing 100,000 map pages (previously taking ~138 hours) required less than 7 hours of automated processing.
2. Performance Metrics:
    * The ensemble model achieved a recall rate of ~90%, meaning it successfully identified the majority of actual manufactured gas plant (MGP) sites.
    * The model demonstrated high accuracy in distinguishing MGP-related circular features from non-MGP infrastructure (e.g, water towers and cisterns).
    * Area Under the Curve (AUC) for the hybrid CNN-MLP model ranged from 0.92 to 0.96 across different test folds, indicating robust classification performance.
3. Detection Improvements:
    * The pipeline identified 23 MGP sites in Washington state across 15 cities, a significant improvement compared to prior studies, which had only identified 14 sites in the entire Pacific Northwest using traditional (read: manual) methods.
4. Pipeline Efficiency:
    * The number of candidate map regions was progressively reduced across the pipeline stages, from 16,393 map pages to 206 final circular candidates, greatly narrowing the scope of required manual validation.
5. Generalizability:
    * The pipeline performed consistently across diverse regions (e.g., Chicago, San Francisco, New Orleans) and map publication years, suggesting that it is adaptable to diverse urban environments and historical contexts.

Potential Improvements and Alternative Approaches

A number of potential improvements and alternative approaches occurred to me while reading this paper. I am by no means an expert in image processing, so I’ll divide these into the “obvious” and those that seem to me as reasonable but are as yet conjecture.

1. “Obvious” Next Steps:
    1. Incorporating Optical Character Recognition (OCR):
        * Adding OCR to detect map labels (e.g., "gasometer" or "gasholder") could complement geometric feature detection, improving in particular the precision of the candidate selection step.
    2. Enhanced Preprocessing:
        * Incorporating multi-scale analysis to detect circular structures of varying sizes and orientations could reduce false positives and improve recall.
        * Making use of alternative circle detection algorithms could improve the efficiency and accuracy of labeling in pre-processing. I found, for instance, that contour-based circular feature identification methods may outperform the Hough transform-based method employed in this paper.
    3. Data Augmentation/Synthetic Data:
        1. I suspect that it would be relatively straightforward to both augment the existing dataset (perhaps improving the detection of circular structures of varying sizes and orientations) and to produce synthetic data from it, providing an expanded training dataset.
    4. Domain-Specific Data Augmentation:
        * Incorporating spatial relationships between detected features (e.g., proximity to industrial zones) into the classification process could enhance model accuracy by aligning predictions with historical urban layouts.
        * 
2. “Less Obvious” Potential Improvements:
    1. Using Transformer-based Models:
        * Transformer architectures, such as Vision Transformers (ViTs), could offer a more sophisticated approach to capturing global contextual information in map images, potentially outperforming CNNs in feature extraction.

Potential Improvements and Alternative Approaches
While reading this paper, several potential improvements and alternative approaches came to mind. I am by no means an expert in image processing, so I’ll divide these into “obvious” next steps, which align with standard extensions to image processing pipelines, and “less obvious” ideas, which are speculative but could perhaps yield improvements.

1. “Obvious” Next Steps
1. Incorporating Optical Character Recognition (OCR):
    * Adding OCR capabilities to detect and interpret textual labels on the maps (e.g., "gasometer," "gasholder") could provide an additional layer of validation for circular features identified as MGP-related.
2. Enhanced Preprocessing:
    * Multi-scale Analysis: Detecting circular structures at varying scales and orientations could mitigate issues arising from varying map resolutions or inconsistently drawn features. This step could help reduce false negatives and improve recall.
    * Alternative Circle Detection Methods: Making use of alternative circle detection algorithms could improve the efficiency and accuracy of labeling in pre-processing. I found, for instance, that contour-based circular feature identification methods may outperform the Hough transform-based method employed in this paper.
3. Data Augmentation and Synthetic Data:
    * I suspect that it would be relatively straightforward to both augment the existing dataset (perhaps improving the detection of circular structures of varying sizes and orientations) and to produce synthetic data from it, providing an expanded training dataset.
4. Domain-Specific Data Integration:
    * Spatial Context Integration: Incorporating spatial relationships between detected features (proximity to industrial zones, for instance) into the classification process could enhance model accuracy by aligning predictions with historical urban layouts.

2. “Less Obvious” Potential Improvements
1. Using Transformer-Based Models:
    * Transformer architectures (such as Vision Transformers (ViTs)) could be used to capture both local and global patterns in the map images. Unlike CNNs (which excel at local feature extraction) ViTs process entire images as sequences of patches, enabling them to model relationships between features across the entire map. This could enhance the model's ability to differentiate between visually similar but contextually distinct features.
2. Hybrid Feature Detection Beyond Circles:
    * While the paper focuses on circular structures, a hybrid approach could integrate the detection of non-circular features like pipelines or building layouts associated with MGPs. Combining geometric and OCR-based analyses might reveal additional contextual clues that current methods overlook.
3. Incorporating Temporal Dynamics:
    * Analyzing multiple editions of maps from different years could help track changes in urban layouts, allowing the model to identify sites that may have been repurposed or demolished. Temporal context could improve recall and provide insights into the historical progression of MGPs.
4. Integration of Bayesian Methods:
    * Adding a Bayesian layer to the model could incorporate prior knowledge about likely MGP locations (e.g., proximity to railways or dense urban centers) into the classification process. I suspect that a probabilistic approach would be particularly useful in ambiguous cases.

# Video: Code & Results Walkthrough

 - [View in repository](assets/code_and_results_walkthrough.mp4)
 - [Watch on YouTube](https://www.youtube.com/watch?v=Ow-c4VDXeEI)


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
-   [Design Considerations](#design-considerations)
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
    

## Design Considerations

The design of this pipeline emphasizes clarity, modularity, and robustness. By adhering to best practices in documentation, modularity, and error handling, the code is both user-friendly and highly maintainable. The components are purposefully structured to work independently, facilitating reuse and adaptation in different workflows beyond the immediate scope of MGP site detection. I have categorized my most significant design considerations as follows. Some of these are obvious, however I will mention them here for completeness.

###  1. **Documentation**

Good code is well-documented. Documentation comprises both an explicit accounting in the form of formal, external documentation (e.g., user guides and, in this case, README files) and inline comments that clarify intent, logic, and complex sections of the code for future maintainers. Well-documented is not synonymous with extensively documented, however, and oftentimes good code explains itself without the need for excessive comments or external documentation. I strove for this by adhering to the following:

  
1. **Explicit Types and Return Types:**
  Using strongly typed variables and annotating functions with explicit return types.

2. **Intuitive Variable and Function Names:**
  Choosing descriptive names that convey the purpose of the variable, function, or class.

3. **Explicit Error and Logging Messages:**
  Employing structured logging and writing detailed error messages that explain what went wrong, where, and (where possible) why.

  Take, for example, the following function. Despite having minimal documentation, it is immediately clear what this function accomplishes and how. The expressive function name, along with explicit argument and return types, obviates the need for a verbose docstring. Intuitive variable names (e.g., `unique_suffix`) further enhance clarity. Making use of such libraries as `pathlib` ensures that the code is expressive and clearly conveys intent:

  

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

---

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
