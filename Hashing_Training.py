import sqlite3
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.random_projection import SparseRandomProjection
from collections import defaultdict
import pickle  # For saving the transformer

# Fetch vectors from SQLite database
def fetch_vectors_from_db(db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT SC, SCvg, SI, SS FROM VectorData")
    rows = cursor.fetchall()

    vectors = [tuple(row) for row in rows]
    connection.close()
    return np.array(vectors)

# Function to compute LSH using cosine similarity with symmetric bucket assignment
def lsh_cosine_hashing(vectors, n_components=4):
    # Use SparseRandomProjection as an approximation for LSH for cosine similarity
    transformer = SparseRandomProjection(n_components=n_components)
    projected_vectors = transformer.fit_transform(vectors)

    # Save the transformer to a file
    with open('transformer.pkl', 'wb') as f:
        pickle.dump(transformer, f)

    # Normalize the projected vectors for cosine similarity
    norms = np.linalg.norm(projected_vectors, axis=1, keepdims=True)
    normalized_vectors = projected_vectors / norms

    # Dictionary to store buckets
    buckets = defaultdict(set)

    # Calculate cosine similarity matrix
    similarity_threshold = 0.999
    similarity_matrix = cosine_similarity(normalized_vectors)

    for i in range(len(normalized_vectors)):
        buckets[i + 1].add(i + 1)  # Ensure each vector includes itself
        for j in range(len(normalized_vectors)):
            if i != j and similarity_matrix[i, j] >= similarity_threshold:
                buckets[i + 1].add(j + 1)

    # Convert sets to sorted lists for consistent storage
    for key in buckets:
        buckets[key] = sorted(buckets[key])

    return buckets, normalized_vectors

# Store hashed vectors in the database
def store_hashed_vectors(db_path, buckets, vectors):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Drop HashedVectors table if it exists
    cursor.execute("DROP TABLE IF EXISTS HashedVectors")

    # Create the HashedVectors table
    cursor.execute("""
        CREATE TABLE HashedVectors (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            OriginalVector TEXT,
            HashedBucket TEXT
        );
    """)

    # Insert each vector and its corresponding hashed bucket into the database
    for vector_idx, neighbors in buckets.items():
        original_vector = str(vectors[vector_idx - 1])
        hashed_bucket = str(neighbors)
        cursor.execute("INSERT INTO HashedVectors (OriginalVector, HashedBucket) VALUES (?, ?)",
                       (original_vector, hashed_bucket))

    connection.commit()
    connection.close()

# Main function to execute LSH hashing and store results
def main():
    db_path = r'C:\Users\Himal\Desktop\Research\srcVul\VectorOperations\SlicingVector_Generator\bin\Debug\net6.0\vectors.db'  # Update this path

    # Step 1: Fetch vectors from the VectorData table
    vectors = fetch_vectors_from_db(db_path)

    # Step 2: Apply LSH using cosine similarity to hash and group vectors into buckets
    buckets, normalized_vectors = lsh_cosine_hashing(vectors)

    # Step 3: Store the hashed vectors into HashedVectors table
    store_hashed_vectors(db_path, buckets, vectors)

    print("LSH hashing with cosine similarity completed and stored in HashedVectors table.")

if __name__ == "__main__":
    main()
