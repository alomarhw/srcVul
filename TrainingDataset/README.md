# TrainingDataset

This folder contains two subfolders:
1. **Snippet**: Contains example snippet, patched code, and slicing profile used to demonstrate vulnerability and corresonding fix as explained in the paper.
2. **Data**: Contains the main dataset in CSV format used for training and evaluating the system.

---

## Snippet Folder

This folder contains the following files:

- **Listing1.txt**:  
  Contains a few lines of code associated with a vulnerability. This file demonstrates an example snippet, referred to as *Figure 2a* in the research paper.

- **Patch.txt**:  
  Contains the patched lines of code corresponding to the vulnerability in `Listing1.txt`. This file is referenced as *Figure 2b* in the paper.

- **SliceProfile_parent.txt**:  
  Contains slicing profiles for the variable `parent`, as referenced in *Figure 4* of the paper.

---

## Data Folder

This folder contains the file:

- **TrainingData.csv**:  
  A CSV file that serves as the main dataset for generating generalized results in the research paper. It includes detailed information about vulnerabilities, projects, slices, and patches in the following format:

  | id | CVE_ID       | Commit_Hash                           | Project               | Vector_Hash                                                     | Slice_Count | Slice_Coverage | Slice_Identifier | Slice_Spatial | Patch_Content                  |
  |----|--------------|---------------------------------------|-----------------------|----------------------------------------------------------------|-------------|----------------|------------------|---------------|--------------------------------|
  | 1  | CVE-2000-0305 | 7954d04a898c040e0e4e2f21b38b0a3b03f68190.diff | openvswitch__ovs    | a825fce8e1c35c0d7be62017cb091aa9c21d689acfac694692bfe2255b5c313d | 0.018867925 | 0.433962264   | 0.830188679      | 0.41509434    | "openvswitch__ovs commit 7954d04a898c040e0e4e2f21b38b0a3b03f68190" |

### Description of Fields in `TrainingData.csv`:

- **id**: Unique identifier for each entry.
- **CVE_ID**: The CVE identifier associated with the vulnerability.
- **Commit_Hash**: The commit hash representing the specific fix for the CVE in the source repository.
- **Project**: The name of the project or system associated with the vulnerability.
- **Vector_Hash**: The hash representing the slicing vector for the vulnerability.
- **Slice_Count**: Number of slices in the final profile for the vulnerability.
- **Slice_Coverage**: Proportion of code covered by the slice relative to the module size.
- **Slice_Identifier**: Count of unique identifiers within the slice.
- **Slice_Spatial**: Spatial distance in lines of code between the first and last use of the slicing variable.
- **Patch_Content**: Details of the patched code for the vulnerability, including the repository commit information.

---

## Purpose

- The **Snippet Folder** provides a simplified demonstration of vulnerabilities and their fixes, as explained in the research paper.
- The **Data Folder** contains the main dataset used for training the system. It allows for generating generalized results and deriving metrics related to vulnerabilities and their patches.

