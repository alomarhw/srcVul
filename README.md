# srcVul
srcVul: Detecting Security Vulnerabilities in Code Clones using Scalable and Efficient Slicing-Based Techniques
srcVul employs a three-stage process to extract non-contiguous, re-ordered, and intertwined vulnerability-related statements (𝑉 𝑅𝑠𝑡𝑚𝑡𝑠) from known vulnerable programs and their corresponding patches for specific known vulnerabilities. The vulnerable program and its patch undergo slicing and comparison to generate a list of vulnerability-related slices (𝑉 𝑅𝑠𝑙𝑖𝑐𝑒𝑠) that contain 𝑉 𝑅𝑠𝑡𝑚𝑡𝑠. These 𝑉 𝑅𝑠𝑙𝑖𝑐𝑒𝑠 are subsequently matched to identify their clones within target program slices. 

SrcVul utilize srcML https://www.srcml.org and srcSlice https://www.srcml.org/tools.html. The gitHub of srcSlice is https://github.com/srcML/srcSlice
