import os
import json
import sqlite3
from glob import glob

# Function to initialize or connect to the vector database and create the TrainingData table
def initialize_vector_database(db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Create the TrainingData table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS TrainingData (
                        id INTEGER PRIMARY KEY,
                        CVE_ID TEXT,
                        Commit_Hash TEXT,
                        Project TEXT,
                        Vector_Hash TEXT,
                        Slice_Count REAL,
                        Slice_Coverage REAL,
                        Slice_Identifier REAL,
                        Slice_Spatial REAL,
                        Patch_Content TEXT
                      )''')
    
    connection.commit()
    return connection, cursor

# Function to insert data into the TrainingData table
def insert_data(cursor, data):
    cursor.execute('''INSERT INTO TrainingData (
                        CVE_ID, Commit_Hash, Project, Vector_Hash,
                        Slice_Count, Slice_Coverage, Slice_Identifier,
                        Slice_Spatial, Patch_Content
                      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                        data["CVE_ID"],
                        data["Commit_Hash"],
                        data["Project"],
                        data["Vector_Hash"],
                        data["Slicing_Vector"]["Slice Count (SC)"],
                        data["Slicing_Vector"]["Slice Coverage (SCvg)"],
                        data["Slicing_Vector"]["Slice Identifier (SI)"],
                        data["Slicing_Vector"]["Slice Spatial (SS)"],
                        data["Patch_Content"]
                      ))

# Function to process all JSON files in a folder and insert them into the database
def process_folder(folder_path, db_path):
    # Initialize the database and get a cursor
    connection, cursor = initialize_vector_database(db_path)

    # Loop over all JSON files in the specified folder
    json_files = glob(os.path.join(folder_path, '*.json'))
    for json_file in json_files:
        with open(json_file, 'r') as f:
            try:
                # Load the JSON data
                data = json.load(f)
                
                # Insert data into the TrainingData table
                insert_data(cursor, data)
                print(f"Inserted data from {json_file}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in {json_file}: {e}")
            except KeyError as e:
                print(f"Missing expected key in {json_file}: {e}")

    # Commit all changes and close the connection
    connection.commit()
    connection.close()
    print("All data has been inserted into the TrainingData table.")

# Main function to execute the process
def main():
    db_path = r'C:\Users\Himal\Desktop\Research\srcVul\VectorOperations\SlicingVector_Generator\bin\Debug\net6.0\vectors.db'  # Update this path
    folder_path = input("Please enter the path to the folder containing the JSON files: ")
    process_folder(folder_path, db_path)

if __name__ == "__main__":
    main()
