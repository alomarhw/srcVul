## Instructions for Running the Python Script

### 1. Open the Script (`SlicingVector_Generator.py`):

- **Run the script using:**
      ```
      python SlicingVector_Generator.py
      ```

### 2. Environment Requirements:

      - Python 3.x
      - `pymongo` library (`pip install pymongo`)
      - MongoDB instance running locally (default URL: `mongodb://localhost:27017/`) or a hosted MongoDB instance (you can update the connection URL accordingly).

### 3. Input Requirements:

- Indicate whether the data is for testing (`yes/no`).  
  If `no` (training), it will ask for:
  - CVE ID
  - Path to the patched version of the code file (used to store the patch content).

- Provide the path to the code file (used to calculate module size).
- Provide the path to the slice profile file.

### 4. Database Output:

The computed metrics are stored in a MongoDB database (`SliceMetricsDB`), in the following collections:

- `VectorData` (for training data)
- `TestVectorData` (for testing data)

Each record contains:

- `Id` (auto-incremented)
- `CVE_ID`
- `SC` (Slice Count)
- `SCvg` (Slice Coverage)
- `SI` (Slice Identifier)
- `SS` (Slice Spatial)
- `MethodName`
- `VariableName`
- `PatchedCode` (only for training data)

### 5. Notes:

- The script will automatically create the collections if they do not exist.
- If the module size or slice profiles are invalid, the script will exit gracefully.
