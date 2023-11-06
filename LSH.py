import numpy as np
from pylsh.lsh import LSH
from pylsh.band import Band
from pylsh.affinity import CosineAffinity
from srcclone import SourceFile

# Define the number of bands and the number of rows per band
num_bands = 8
num_rows = 16

# Load your slicing vectors into a list
# Each vector should be a list or numpy array of floating-point values
slicing_vectors = [
    [1.0, 0.5, 0.7, 0.3, 0.2],
    # Add more slicing vectors here...
]

# Create an LSH model with cosine similarity
lsh = LSH(num_bands, num_rows, affinity=CosineAffinity())

# Hash the slicing vectors
for i, vector in enumerate(slicing_vectors):
    lsh.index(i, vector)

# Get the candidate pairs using LSH
candidate_pairs = lsh.query_candidates()

# Initialize a list to store source files
source_files = []

# Create source files from the candidate pairs
for i, j in candidate_pairs:
    source_file_i = SourceFile(slicing_vectors[i])
    source_file_j = SourceFile(slicing_vectors[j])
    source_files.append(source_file_i)
    source_files.append(source_file_j)

# Identify clones using srcClone
from srcclone.srcclone import SrcClone
from srcclone.config import SimMeasure, CloneDetectMethod

src_clone = SrcClone(source_files, threshold=0.8, sim_measure=SimMeasure.HASHING, detect_method=CloneDetectMethod.EXACT, force_exe=True)
src_clone.run()

# Display the clone pairs
print("Clone Pairs:")
for clone_pair in src_clone.get_clone_pairs():
    print(f"Clone Pair {clone_pair.id} - Similarity: {clone_pair.similarity}")
    print(clone_pair.file1.contents)
    print(clone_pair.file2.contents)
    print()
