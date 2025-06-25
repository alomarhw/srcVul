# TestingDataset

This folder contains two subfolders:
1. **Snippet**: Contains target example snippet explained in the paper.
2. **Data**: Contains testing datasets for four different systems.
3. **Slices**: Contains the slices for the testing systems.

## Snippet Folder
This folder contains the following files:
- **Figure5.txt**:  
  Contains a few lines of code to be tested for vulnerability.  
  This file demonstrates an example snippet (Figure 5) explained in the research paper.

- **SliceProfile_parent.txt**:  
  Contains slice profiles for the variable `parent`.  
  This file is linked to the example snippet (Figure 6) in the paper.

## Data Folder
This folder contains the following files:
- **libgd-2.3.0.tar.gz**: Testing data for the `libgd` system.
- **libvirt-1.1.0.tar.gz**: Testing data for the `libvirt` system.
- **linux-4.14.76.tar.gz**: Testing data for the `Linux` system.
- **samba-4.0.26.tar.gz**: Testing data for the `Samba` system.

## Slices Folder
This folder contains the following files:
- **libvirt-1.1.0.slice.xml**: Slices generated from srcSlice for the `libvirt` system.
- Since the other systems are too large to upload to the GitHub repository, we have provided a Google Drive link:
 [Download Large Slices Files]( https://drive.google.com/drive/folders/11ycRBv6Wr3W6lCHLRxJ1LnQwCAywX2Jp)

Each file provides testing datasets and real-world systems that were analyzed for vulnerabilities.



