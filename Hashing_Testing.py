import sqlite3
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.random_projection import SparseRandomProjection
from collections import defaultdict
import pickle

# Fetch vectors from SQLite database for testing
def fetch_test_vectors_from_db(db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT SC, SCvg, SI, SS FROM TestVectorData")  # Table for target/test vectors
    rows = cursor.fetchall()
    
    print(f"Fetched {len(rows)} test vectors from TestVectorData.")  # Debugging statement

    vectors = [tuple(row) for row in rows]
    connection.close()
    return np.array(vectors)

# Function to process test vectors using pre-fitted transformer and normalized train vectors
def process_test_vectors(test_vectors, transformer, normalized_train_vectors, similarity_threshold=0.45):
    # Project test vectors using the pre-fitted transformer
    projected_test_vectors = transformer.transform(test_vectors)

    # Normalize test vectors
    norms = np.linalg.norm(projected_test_vectors, axis=1, keepdims=True)
    normalized_test_vectors = projected_test_vectors / norms

    # Compare test vectors with train vectors
    results = defaultdict(list)
    similarity_matrix = cosine_similarity(normalized_test_vectors, normalized_train_vectors)

    # Track similarity scores for analysis
    similarities = []

    print("Starting similarity comparison between test and train vectors...")

    for i, test_vector in enumerate(normalized_test_vectors):
        for j, train_vector in enumerate(normalized_train_vectors):
            sim = similarity_matrix[i, j]
            similarities.append(sim)
            if sim >= similarity_threshold:
                results[i + 1].append(j + 1)
                print(f"Match: Test Vector {i+1} is similar to Train Vector {j+1} with similarity {sim:.4f}")

    # Calculate similarity statistics
    if similarities:
        print(f"Max similarity score: {max(similarities):.4f}")
        print(f"Min similarity score: {min(similarities):.4f}")
        print(f"Average similarity score: {np.mean(similarities):.4f}")
    else:
        print("No similarities found.")

    print(f"Total matches found: {sum(len(v) for v in results.values())}")
    return results


# Store test vector results in the database
def store_test_results(db_path, results, test_vectors):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Create the TestResults table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TestResults (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            TestVector TEXT,
            SimilarTrainBuckets TEXT
        );
    """)

    # Insert each test vector and its corresponding similar train buckets into the database
    print(f"Inserting results into TestResults table. Total test vectors with matches: {len(results)}")  # Debugging
    for test_idx, similar_buckets in results.items():
        test_vector = str(test_vectors[test_idx - 1])
        similar_buckets_str = str(similar_buckets)
        cursor.execute("INSERT INTO TestResults (TestVector, SimilarTrainBuckets) VALUES (?, ?)",
                       (test_vector, similar_buckets_str))
        print(f"Inserted Test Vector {test_idx} with similar buckets: {similar_buckets}")  # Debugging

    connection.commit()
    print("All results committed to the database.")  # Debugging
    connection.close()

# Main function to process and store test results
def main():
    db_path = r'C:\Users\Himal\Desktop\Research\srcVul\VectorOperations\SlicingVector_Generator\bin\Debug\net6.0\vectors.db'  # Update this path

    # Step 1: Load the pre-fitted transformer
    try:
        with open('transformer.pkl', 'rb') as f:
            transformer = pickle.load(f)
        print("Transformer loaded successfully.")  # Debugging statement
    except FileNotFoundError:
        print("Error: transformer.pkl file not found.")  # Debugging
        return

    # Step 2: Fetch normalized training vectors from HashedVectors table
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT OriginalVector FROM HashedVectors")
    rows = cursor.fetchall()
    connection.close()

    print(f"Fetched {len(rows)} training vectors from HashedVectors.")  # Debugging statement

    # Process OriginalVector to handle missing commas
    try:
        normalized_train_vectors = np.array([
            np.fromstring(row[0].strip('[]'), sep=' ') for row in rows
        ])
    except ValueError as e:
        print("Error processing training vectors:", e)
        return

    # Step 3: Fetch vectors from the TestVectorData table
    test_vectors = fetch_test_vectors_from_db(db_path)

    # Step 4: Process test vectors against the normalized training vectors
    results = process_test_vectors(test_vectors, transformer, normalized_train_vectors)

    # Step 5: Store the test results into TestResults table
    store_test_results(db_path, results, test_vectors)

    print("Testing completed and results stored in TestResults table.")

if __name__ == "__main__":
    main()
