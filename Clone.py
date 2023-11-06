from sklearn.neighbors import LSHForest
import numpy as np

# Example vectors for demonstration (replace with your actual vectors)
vectors = [
    [0.1, 0.2, 0.3],
    [0.15, 0.18, 0.28],
    [0.09, 0.22, 0.31],
    [0.12, 0.19, 0.29],
    # Add more vectors here
]

# Convert the vectors to a NumPy array
vectors = np.array(vectors)

# Set the number of hash tables and number of neighbors to search
n_neighbors = 5  # Adjust as needed
n_estimators = 20  # Adjust as needed

# Create an LSHForest and fit it with the vectors
lshf = LSHForest(n_neighbors=n_neighbors, n_estimators=n_estimators)
lshf.fit(vectors)

# Query for nearest neighbors to find code clones
similar_indices = lshf.kneighbors(vectors, return_distance=False)

# Define a threshold to determine similarity (adjust as needed)
similarity_threshold = 0.9

# Find code clones based on similarity threshold
code_clones = []
for i, neighbors in enumerate(similar_indices):
    for j in neighbors:
        if i < j and vectors[i].dot(vectors[j]) / (np.linalg.norm(vectors[i]) * np.linalg.norm(vectors[j])) >= similarity_threshold:
            code_clones.append((i, j))

# Print the detected code clones
for clone in code_clones:
    print(f"Code Clone Detected between vectors {clone[0]} and {clone[1]}")

# You can now analyze and inspect the code clones further
