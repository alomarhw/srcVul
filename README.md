# srcVul
srcVul: Detecting Security Vulnerabilities in Code Clones using Scalable and Efficient Slicing-Based Techniques

The srcVul system is designed to identify security vulnerabilities in code clones using a methodical three-stage process. It focuses on extracting non-contiguous, re-ordered, and intertwined statements related to vulnerabilities (𝑉 𝑅𝑠𝑡𝑚𝑡𝑠) from well-documented vulnerable programs and their corresponding patches for specific known vulnerabilities. This process includes:

Slicing and Comparison: The vulnerable program and its associated patch are subjected to slicing and comparison. This stage is crucial in generating a list of vulnerability-related slices (𝑉 𝑅𝑠𝑙𝑖𝑐𝑒𝑠) that contain 𝑉 𝑅𝑠𝑡𝑚𝑡𝑠.
Cloning Detection: The 𝑉 𝑅𝑠𝑙𝑖𝑐𝑒𝑠, obtained from the previous stage, are systematically compared to pinpoint their clones within slices of the target program.
To achieve this, srcVul leverages the capabilities of srcML (available at https://www.srcml.org) and srcSlice (found at https://www.srcml.org/tools.html). Additionally, the source code of srcSlice can be accessed on GitHub at https://github.com/srcML/srcSlice.
