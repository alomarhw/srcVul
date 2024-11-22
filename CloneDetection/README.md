# Clone Detection Script

This folder contains a Python script that processes JSON files with slicing vectors associated with CVE identifiers. The script utilizes **MinHash** and **Locality-Sensitive Hashing (LSH)** to identify and group vulnerabilities with similar slicing vectors (i.e., potential clones). 

---

## Features

1. **Identify Clones**:  
   Detect vulnerabilities (CVE IDs) with similar slicing vectors.
   
2. **Group Clones**:  
   Group CVEs into "clone groups" where the slicing vectors are highly similar.
   
3. **Find Clone Pairs**:  
   Identify pairs of CVEs that have a high similarity score based on their slicing vectors.
   
4. **Output Results**:  
   Save clone groups and clone pairs into separate files for further analysis.

---

## How It Works

### 1. Input Data
- **Source**: JSON files in the specified directory (`PATCH_METADATA_PATH`).
- **File Structure**:  
  Each JSON file represents a vulnerability (e.g., `CVE-XXXX-XXXX.json`) and contains:
  - `CVE_ID`: The unique identifier for the vulnerability.
  - `Slicing_Vector`: A dictionary representing the slicing vector for the CVE.

---

### 2. MinHash Representation
- **Purpose**: Convert slicing vectors into compact MinHash signatures for efficient comparison.  
- **Steps**:
  - Each key-value pair in the slicing vector is converted into a string (`key:value`).
  - The string is hashed using MinHash to create a 128-dimensional signature.

---

### 3. LSH Index
- **Purpose**: Use Locality-Sensitive Hashing to quickly find slicing vectors that are similar.  
- **Steps**:
  - Insert each MinHash signature into an LSH index, using the CVE ID as its identifier.
  - The LSH index enables efficient querying for similar slicing vectors.

---

### 4. Find Clone Groups and Pairs
#### Clone Groups:
- For each CVE, query the LSH index to find other CVEs with similar slicing vectors.
- Group these CVEs into "clone groups" if they have a similarity score above the threshold (0.8).
- Only groups with more than one member are saved.

#### Clone Pairs:
- Record unique pairs of CVEs that are highly similar (e.g., `(CVE-A, CVE-B)`).

---

### 5. Avoid Duplicates
The script keeps track of already processed CVEs to avoid re-querying and inserting duplicate entries.

---

### 6. Output Results
#### **Clone Groups**:
- Contains groups of CVEs with highly similar slicing vectors.
- Saved in `clone_groups.txt` with each group listed sequentially.  
- **Example**:
  Clone Group: CVE-2021-0001, CVE-2021-0002
  Clone Group: CVE-2020-1234, CVE-2020-5678

  Total number of clone groups: 2


#### **Clone Pairs**:
- Contains pairs of CVEs with similarity above the threshold.
- Saved in `clone_pairs.txt`.  
- **Example**:
  Clone Pair: CVE-2021-0001, CVE-2021-0002
  Clone Pair: CVE-2020-1234, CVE-2020-5678

  Total number of clone pairs: 2


---

## Practical Applications

1. **Clone Detection**:  
 Identify similar vulnerabilities to study patterns or relationships between them.  
 Useful for detecting vulnerabilities with similar root causes or remediation patterns.

2. **Slicing Vector Analysis**:  
 Analyze slicing vectors to determine structural or behavioral similarities in code vulnerabilities.

3. **Patch Recommendations**:  
 When two CVEs are highly similar, patches for one CVE may be applicable to another.

4. **Efficiency**:  
 The use of MinHash and LSH enables scalable and efficient detection of clones, even with large datasets of slicing vectors.

---

## Dependencies

1. **Python Libraries**:
 - `datasketch`: For MinHash and LSH functionalities.
 - `os` and `json`: For file handling and JSON parsing.

2. **Input Data**:  
 JSON files containing slicing vectors and associated CVE IDs.

3. **Configuration**:  
 Modify the following paths in the script to match your environment:
 - `PATCH_METADATA_PATH`: Path to the folder containing JSON files.
 - `GROUPS_OUTPUT_PATH`: Path to save `clone_groups.txt`.
 - `PAIRS_OUTPUT_PATH`: Path to save `clone_pairs.txt`.

---

## Usage

1. Place the JSON files containing slicing vectors in the directory specified by `PATCH_METADATA_PATH`.
2. Run the script.
3. The outputs (`clone_groups.txt` and `clone_pairs.txt`) will be saved in the paths specified by `GROUPS_OUTPUT_PATH` and `PAIRS_OUTPUT_PATH`.


