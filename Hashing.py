import sqlite3
import numpy as np
from collections import defaultdict

# Function to calculate Euclidean distance between two vectors
def euclidean_distance(v1, v2):
    return np.linalg.norm(np.array(v1) - np.array(v2))

# Function to create hash buckets based on Euclidean distance
def hash_vectors(vectors, threshold=0.2):
    buckets = defaultdict(list)  # Buckets to store hashed vectors
    hash_id = 0                  # Start with the first bucket

    for i, vec1 in enumerate(vectors):
        # Try to place the vector in an existing bucket
        placed = False
        for key, bucket in buckets.items():
            # Compare vec1 with any vector already in the bucket
            if any(euclidean_distance(vec1, vec2) <= threshold for vec2 in bucket):
                buckets[key].append(vec1)  # Add vector to the existing bucket
                placed = True
                break
        
        # If the vector doesn't fit any existing bucket, create a new bucket
        if not placed:
            buckets[hash_id].append(vec1)
            hash_id += 1

    return buckets

def fetch_vectors_from_db(db_path):
    # Connect to the database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Fetch vectors from VectorData table
    cursor.execute("SELECT SC, SCvg, SI, SS FROM VectorData")
    rows = cursor.fetchall()

    # Convert rows to a list of vectors
    vectors = [tuple(row) for row in rows]

    connection.close()
    return vectors

def insert_hashed_vectors(db_path, buckets):
    # Connect to the database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Create the HashedVectors table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS HashedVectors (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Vector TEXT,
            HashedVector INTEGER
        );
    """)

    # Insert vectors and their corresponding hash (bucket) into the HashedVectors table
    for hash_id, vectors in buckets.items():
        for vector in vectors:
            cursor.execute("INSERT INTO HashedVectors (Vector, HashedVector) VALUES (?, ?)", 
                           (str(vector), hash_id))

    # Commit and close
    connection.commit()
    connection.close()

def main():
    db_path = r'C:\Users\Himal\Desktop\Research\srcVul\SlicingVector_Generator\SlicingVector_Generator\bin\Debug\net6.0\vectors.db'  # Path to SQLite database
    #TODO - update the instruction for providing path

    # Step 1: Fetch vectors from the VectorData table
    vectors = fetch_vectors_from_db(db_path)

    # Step 2: Hash the vectors into buckets based on Euclidean distance
    buckets = hash_vectors(vectors, threshold=0.2)

    # Step 3: Insert the hashed vectors into the HashedVectors table
    insert_hashed_vectors(db_path, buckets)

    print("Hashing completed and stored in HashedVectors table.")

if __name__ == "__main__":
    main()
