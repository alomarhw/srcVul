## Instructions for Running the C# Solution

### 1. Open the Solution File (`SlicingVector_Generator.sln`):

- **In Visual Studio Code:**
  - Open the folder containing the solution file in VS Code.
  - Install the C# extension by Microsoft (if not already installed).
  - Press `Ctrl + F5` to run the project without debugging, or click the Run button in the toolbar.

- **In Visual Studio:**
  - Open the solution file.
  - Build the solution (`Ctrl + Shift + B`) and run it (`F5`).

### 2. Input Requirements:

- Indicate whether the data is for testing (`yes/no`).  
  If `no` (training), it will ask for the path to the patched file as the third input.
- Provide the path to the code file (used to calculate module size).
- Provide the path to the slice profile file.

### 3. Database Output:

The metrics (SC, SZ, SCvg, SI, SS) are stored in an SQLite database (`vectors.db`), with the following fields:

- `MethodName`
- `VariableName`
- `SC` (Slice Count)
- `SZ` (Slice Size)
- `SCvg` (Slice Coverage)
- `SI` (Slice Identifier)
- `SS` (Slice Spatial)
- `Patched Text` (if it’s training data)
