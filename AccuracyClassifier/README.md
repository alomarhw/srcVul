# Accuracy Classifier Script

This folder contains a Python script for evaluating the accuracy of vulnerability detection by classifying results into True Positives (TP), False Positives (FP), True Negatives (TN), and False Negatives (FN) using slicing vectors.

---

## Features

1. **Classify Vulnerabilities**:
Classifies vulnerabilities into True Positives, False Positives, True Negatives, and False Negatives based on slicing vector hashes.

2. **Track Detection Accuracy**:
Tracks the accuracy of vulnerability detection by comparing diff and patch metadata files to known vulnerabilities.

3. **Output Results**:
Prints the counts of TP, FP, TN, and FN along with the IDs of the corresponding files.

---

## How It Works

### 1. Input Data
- **Source**: Diff files in the specified directory (CVE_DIFFS_PATH) and patch metadata files in (PATCH_METADATA_PATH).

- **File Structure**:

  - .diff files represent changes between different versions of the code.

  - .json files in patch_metadata contain metadata for known CVE patches.

---

### 2. Slicing Vector Detection
- **Purpose**: Analyze diffs between code versions and generate slicing vectors based on vulnerability-related code changes.

- **Steps**:

  - Each diff is processed to generate slicing vectors.

  - These vectors are compared against a database of known slicing vectors (from the patch metadata) to detect vulnerabilities.

### 3. Classification
- **Purpose**: Classify each detected vulnerability as TP, FP, TN, or FN based on its similarity to the known vulnerability database.

- **Steps**:

  - If a detected vulnerability matches an existing one (using slicing vectors), it's classified as TP.

  - If it doesn't match, it's classified as FN (for true vulnerabilities that were missed).

  - Non-CVE diffs are checked for false positives (FP) or true negatives (TN).

### 4. Output Results
  **True Positives (TP)**:
    Correctly detected vulnerabilities.
  
  **False Negatives (FN)**:
    Missed vulnerabilities.
  
  **False Positives (FP)**:
    Incorrectly detected vulnerabilities.
  
  **True Negatives (TN)**:
    Correctly identified non-vulnerabilities.
  
  **Example Output**:
  
    - True Positives (TP): 12
    - False Negatives (FN): 4
    - False Positives (FP): 3
    - True Negatives (TN):  1
  
    Final Counts:
      - Total True Positives (TP): 12
      - TP IDs: ['file1.diff', 'file2.diff', ...]
      
      - Total False Negatives (FN): 4
      - FN IDs: ['file3.diff', 'file4.diff', ...]
      
      - Total False Positives (FP): 3
      - FP IDs: ['file5.diff', 'file6.diff', ...]
      
      - Total True Negatives (TN): 1
      - TN IDs: ['file7.diff']

---

## Dependencies

1. **Python Libraries**:

    os, re, json, shutil, hashlib, datetime, collections

2. **Input Data**:

    - Diff files in CVE_DIFFS_PATH directory.
    
    - JSON files containing patch metadata in PATCH_METADATA_PATH directory.

3. **Configuration**:

    Modify the following paths in the script to match your environment:
  
    - `CVE_DIFFS_PATH`: Path to the directory containing diff files.
    
    - `PATCH_METADATA_PATH`: Path to the directory containing patch metadata files.
    
    - 'UNIQUE_PATCH_METADATA_PATH`: Path to the directory storing unique patch metadata.

---

## Usage

1. **Run the Script**:
  Execute the following command:
  - python Positives_Negatives_Classifier.py
  
2. **Enter Paths**:
  The script will prompt you to input the following paths:

  - CVE Diff Directory: Path to the directory containing .diff files (e.g., /Users/gyawalh/srcVul/CVE_Diffs).

  - Patch Metadata Directory: Path to the directory containing .json metadata files (e.g., /Users/gyawalh/srcVul/patch_metadata).
  
  - Unique Patch Metadata Directory: Path to store unique metadata for testing purposes (e.g., /Users/gyawalh/srcVul/unique_patch_metadata).

3. **Results**:
  After processing, the script will display the classification results and output the IDs of the files categorized as TP, FP, FN, or TN.
